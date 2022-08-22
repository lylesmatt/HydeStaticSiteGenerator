import mimetypes
import shutil
from abc import ABC, abstractmethod
from io import StringIO
from logging import getLogger
from pathlib import Path
from typing import IO, Iterable, Optional, Union

import yaml
from liquid import Context, Environment, FileSystemLoader, Mode
from liquid.context import ReadOnlyChainMap
from liquid.exceptions import Error
from liquid.loaders import TemplateSource

logger = getLogger('hyde')

PathType = Union[Path, str]


def get_content_type(path: PathType) -> Optional[str]:
    try:
        return mimetypes.guess_type(str(path))[0]
    except:
        return None


class FrontMatterTemplateParseException(Error):
    """Exception raised when front matter template cannot be parsed"""


class FrontMatterAwareFileSystemLoader(FileSystemLoader):
    front_matter_indicator = '---\n'

    def __init__(self, search_path: Union[str, Path, Iterable[Union[str, Path]]], encoding: str = 'utf-8'):
        super().__init__(search_path, encoding)

    def get_source(self, env: Environment, template_name: str) -> TemplateSource:
        orig_src: TemplateSource = super().get_source(env, template_name)
        try:
            if orig_src.source.startswith(self.front_matter_indicator):
                _, front_matter_content, new_source = orig_src.source.split(self.front_matter_indicator, 2)
                front_matter = yaml.safe_load(front_matter_content)

                page_matter = dict()
                matter = {'page': page_matter}
                for key, value in front_matter.items():
                    if key.startswith('$'):
                        matter[key] = value
                    else:
                        page_matter[key] = value

                return TemplateSource(
                    source=new_source,
                    filename=orig_src.filename,
                    uptodate=orig_src.uptodate,
                    matter=matter
                )
        except Exception as ex:
            logger.error('Unable to parse front matter from template', exc_info=ex)
            if env.mode == Mode.STRICT:
                raise FrontMatterTemplateParseException() from ex
        return orig_src


class SiteDestination(ABC):
    @abstractmethod
    def write_file(self, file_path: Path, content_type: str, content: IO) -> None: ...

    def clean(self) -> None: ...


class NoOpSiteDestination(SiteDestination):
    def write_file(self, file_path: Path, content_type: str, content: IO) -> None:
        print(file_path, content_type)


class FileSystemSiteDestination(SiteDestination):
    def __init__(self, base_path: PathType) -> None:
        super().__init__()
        self.base_path = Path(base_path)

    def write_file(self, file_path: Path, content_type: str, content: IO) -> None:
        full_path = self.base_path.joinpath(file_path)
        full_path.parent.mkdir(exist_ok=True)
        mode = 'w' if content_type.startswith('text/') else 'wb'
        with full_path.open(mode=mode) as f:
            f.write(content.read())

    def clean(self) -> None:
        shutil.rmtree(self.base_path)


class Hyde:
    def __init__(self, root_path: PathType = None, site_destination: SiteDestination = None) -> None:
        super().__init__()
        self.src_path = Path(root_path) if root_path else Path.cwd()
        self.data_path = self.src_path.joinpath('_data')
        self.site_destination = site_destination or FileSystemSiteDestination(self.src_path.joinpath('_site'))
        layout_path = self.src_path.joinpath('_layouts')
        loader = FrontMatterAwareFileSystemLoader(search_path=[self.src_path, layout_path])
        self.liquid_env = Environment(loader=loader, globals={'data': {}})

    def clean_site(self) -> None:
        self.site_destination.clean()

    def generate_site(self) -> None:
        for data_file in self.data_path.glob('*.yaml'):
            with data_file.open('r') as f:
                data_name = data_file.name.removesuffix('.yaml')
                data_values = yaml.safe_load(f)
                self.liquid_env.globals['data'][data_name] = data_values

        for path in self.src_path.glob('**/*.*'):
            if self._ignore_file(path):
                continue
            content_type = get_content_type(path)
            if content_type:
                rel_path = path.relative_to(self.src_path)
                if content_type.startswith('text/'):
                    rendered_content = self._render_liquid_template(rel_path)
                    self.site_destination.write_file(rel_path, content_type, rendered_content)
                else:
                    with path.open('rb') as f:
                        self.site_destination.write_file(rel_path, content_type, f)

    def _ignore_file(self, path: Path) -> bool:
        for parent in path.parents:
            if parent.name.startswith('_'):
                return True
        return False

    def _render_liquid_template(self, template_name: PathType) -> IO:
        template = self.liquid_env.get_template(str(template_name))
        context = Context(self.liquid_env, globals=ReadOnlyChainMap(template.matter, template.globals))
        content = StringIO()
        template.render_with_context(context=context, buffer=content)
        layout = context.globals.get('$layout')
        if layout:
            layout_template = self.liquid_env.get_template(layout + '.html')
            layout_content = StringIO()
            layout_template.render_with_context(context=context, buffer=layout_content, content=content.getvalue())
            layout_content.seek(0)
            return layout_content
        else:
            content.seek(0)
            return content
