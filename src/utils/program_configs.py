import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import tomllib

import dacite
import tomlkit.toml_file
import typer
from dacite import Config
from tomlkit import document, TOMLDocument, comment
from tomlkit import table
from tomlkit.items import Table

APP_NAME = "cfcc"

@dataclass
class CodeforcesConfig:
    url:str = "https://codeforces.com"
    user_agent:str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    program_language: str = "C++23"
    prefer_browser_cookies:str|None = None

    def get_as_toml_table(self) -> Table:
        cf_config = table()
        cf_config.add(comment("Configuration related to Codeforces scraping."))
        cf_config.add("url", self.url)
        cf_config["url"].comment("Codeforces URL.")
        cf_config.add("user_agent", self.user_agent)
        cf_config["user_agent"].comment("User agent to use for scraping.")
        cf_config.add("program_language", str(self.program_language))
        cf_config["program_language"].comment("Program language use by codeforces to compile your code, you can find all available languages here: https://github.com/ThorTuwy/cfcc/blob/master/src/utils/language_to_program_id.py")
        if self.prefer_browser_cookies:
            cf_config.add("prefer_browser_cookies", self.prefer_browser_cookies)
        else:
            cf_config.add("prefer_browser_cookies", "None")
        cf_config["prefer_browser_cookies"].comment("Select what browser you want to use for cookies. (Brave, Chrome, Chromium, Firefox)")
        return cf_config

@dataclass
class CodeConfig:
    compile_command:str = "g++ -Wall -Wextra -Wshadow -Wfloat-equal -fsanitize=address -fsanitize=undefined -fno-sanitize-recover=undefined -std=c++23 -o problem"""
    template_file_path:Path = Path("template.cpp")

    def get_as_toml_table(self) -> Table:
        code_config = table()
        code_config.add(comment("Configuration related to code/compilation."))
        code_config.add("compilation_command", self.compile_command)
        code_config["compilation_command"].comment("Compilation command to use for compiling the code. (Your output MUST be ./problem)")
        code_config.add("template_file", str(self.template_file_path))
        code_config["template_file"].comment("Path to the template file to use for the problems.")
        return code_config

@dataclass
class ProgramConfigs:
    codeforces_config:CodeforcesConfig
    code_config:CodeConfig

    @classmethod
    def regenerate_config(cls):
        config_path = Path(typer.get_app_dir(APP_NAME))
        if config_path.exists():
            shutil.rmtree(config_path)
        config_path.mkdir(parents=True, exist_ok=True)

        config_file_path = config_path / "config.toml"
        default_configs_doc = cls.generate_default_toml_doc()

        config_file_toml = tomlkit.toml_file.TOMLFile(config_file_path)
        config_file_toml.write(default_configs_doc)

        shutil.copy(Path(__file__).parent / "default_template.cpp", config_path / CodeConfig.template_file_path)



    @classmethod
    def get_program_config(cls) -> ProgramConfigs:
        config_path = Path(typer.get_app_dir(APP_NAME))
        config_path.mkdir(parents=True, exist_ok=True)
        config_file_path = config_path / "config.toml"
        config_file_toml = tomlkit.toml_file.TOMLFile(config_file_path)

        if not config_file_path.exists():
            default_configs_doc=cls.generate_default_toml_doc()
            config_file_toml.write(default_configs_doc)

        config_data = config_file_toml.read().unwrap()
        config:ProgramConfigs = dacite.from_dict(data_class=ProgramConfigs, data=config_data)

        template_file_path = Path(config.code_config.template_file_path)
        if not template_file_path.is_absolute():
            template_file_path = config_path / template_file_path

        if not template_file_path.exists():
            if not template_file_path.parent.exists():
                raise FileNotFoundError(f"Template file folder {template_file_path.parent} not found")
            shutil.copy(Path(__file__).parent / "default_template.cpp", template_file_path)
            os.chmod(template_file_path, 0o644)

        config.code_config.template_file_path = template_file_path

        if config.codeforces_config.prefer_browser_cookies=="None":
            config.codeforces_config.prefer_browser_cookies=None

        return config

    @classmethod
    def generate_default_toml_doc(cls) -> TOMLDocument:
        default_config = ProgramConfigs(CodeforcesConfig(), CodeConfig())
        return default_config.get_as_toml_doc()

    def get_as_toml_doc(self) -> TOMLDocument:
        doc = document()
        doc.add("codeforces_config",self.codeforces_config.get_as_toml_table())
        doc.add("code_config",self.code_config.get_as_toml_table())
        return doc


def load_general_config_file() -> Dict[str,Any]:
    config_file = Path(typer.get_app_dir(APP_NAME)) / "config.toml"

    config_file.parent.mkdir(parents=True,exist_ok=True)

    if not config_file.exists():
        open(config_file,"x")

    with config_file.open("rb") as f:
        config = tomllib.load(f)

    template_file = Path(typer.get_app_dir(APP_NAME)) / "template.cpp"
    if not template_file.exists():
        open(template_file,"x")

    if "code" not in config:
        config["code"] = {}
    config["code"]["template_file"] = str(template_file.resolve())
    return config