import os
from jinja2 import Environment, FileSystemLoader
import base64
from dotenv import dotenv_values
from config import TemplateConfig
from typing import List, Optional, Callable
from config import TemplateConfig, template_configs

env = dotenv_values('.env')
# env = dotenv_values(os.path.join('..', 'backend', '.env'))

def get_configs() -> List[TemplateConfig]:
    return template_configs

# Function to base64 encode a value
def b64encode(value):
    return base64.b64encode(value.encode('utf-8')).decode('utf-8')

def apply_filters(env: Environment, filters: List[Callable[[str], str]]) -> None:
    if filters:
        for filter_func in filters:
            print (f'filter_func: {filter_func.__name__}')   
            env.filters[filter_func.__name__] = filter_func

def create_yaml(
    config: TemplateConfig, 
    data_provider: callable, 
    template_dir: str, 
    template_name: str, 
    output_filename: str,
    filters: Optional[List[Callable[[str], str]]] = None,
) -> None:

    env = Environment(loader=FileSystemLoader(template_dir))

    apply_filters(env, filters)

    template = env.get_template(template_name)
    
    output_file = os.path.join(config.service_name, output_filename)

    print(f'Generating YAML for {config.service_name}...')
    rendered_yaml = template.render(data_provider())
    
    with open(output_file, 'w') as f:
        f.write(rendered_yaml)
    
    print(f'YAML generated and saved to {output_file}')

for config in get_configs():
    template_dir = 'templates'

    if config.get_secrets_data():
        create_yaml(config=config, 
                    data_provider=config.get_secrets_data, 
                    template_dir=template_dir, 
                    template_name='secret_template.yaml.j2',
                    output_filename=config.service_name + '-secret.yaml',
                    filters=[b64encode])

    if config.get_config_data():
        create_yaml(config=config, 
                    data_provider=config.get_config_data, 
                    template_dir=template_dir, 
                    template_name='config_map_template.yaml.j2',
                    output_filename=config.service_name + '-config.yaml')