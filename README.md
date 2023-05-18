# irails
A mvc framework used FastApi
Simple and elegant use of FastApi in MVC mode

[Online Docs](https://irails.2rails.cn/) 
# Welcome to IRAILS(python on rails)
IRAILS is not just an ordinary imitation of Ruby on rails, but based on the characteristics of the Python language itself, combined with rich Python class libraries, it refuses to create wheels repeatedly, and can achieve web development with minimal code and configuration, making Python web development fast and powerful, and can be easily deployed on various platforms.
The design concept of IRails refers to some RORs, but it has its own soul. It does not pursue the ultimate configuration and development, but rather appropriate configuration and development. Currently, it is in a preview version and will continue to improve in the future.
 

## Installation  

* `pip install irails` - install irails

## Commands

* `irails project [project-name(dir-name)]`         - Create a new irails project.
* `irails app [app-name(choose or input apps dir)]` - Example: `irails app admissions` Create a new irails app.
* `irails run [--host host] [--port port]`          - Run project visit on [http://127.0.0.1:8000>](http://127.0.0.1:8000). 
* `irails controller [actions...]`                  - generate a controller with given actions(if no given,defalut is **index**). 
* `irails model [columns...]`                       - generate a model(and model's service and tests) with given columns(if no given,defalut is **id**). 
 

## Project layout
```
 
    |   main.py
    +---apps                                ## Apps container (A project can have multiple containers)
    |   +---admissions                      ## App dir (An application container can have multiple applications)
    |   |   |   __init__.py                 
    |   |   +---controllers                 ## Controller files
    |   |   |   |   home_controller.py      ## Controller class file,it's look like `class HomeController`
    |   |   |   |   __init__.py
    |   |   +---locales                     ## I18n locales dir,use command `apps/app:$ iralis i18n gettext` will auto generate items
    |   |   +---models                      ## Database models files(if you use some database support)
    |   |   |       __init__.py
    |   |   +---services                    ## Module for business logic processing
    |   |   +---tests                       ## Unit testting
    |   |   +---views                       ## Static view files (use `Jinja2` Template)
    |   |   |   |   layout.html
    |   |   |   |
    |   |   |   +---home                    ## The controller action's static file(name is same to the controller's class name)
    |   |   |   |       home.css            
    |   |   |   |       home.html           ## Static file corresponding to action(name is same to the controller's method name)
    +---configs                             ## Project configure dir
    |       alembic.ini                     ## Alembic configure file (Generally, there is no need to change, used the database migration)
    |       casbin-adapter.csv              ## Casbin auth module config adapter file()
    |       casbin-model.conf               ## Casbin auth config model
    |       database.yaml                   ## Configure for database support
    |       general.yaml                    ## General configures
    |       session.yaml                    ## Session configures
    |
    +---data
    |   +---alembic
    |   |   \---versions
    |   \---db
    |
    +---public                              ## Public dir (will mounted to the '/public' url)
    |   |   error_404.html                  ## Error page ...
    |   |   error_500.html
    |
    +---uploads                             ## Others dir(if your need or not)
```
## Extras commands
* `irails i18n gettext`  --generate i18n in irails app dir
* `irails shell`         --run python interpreter with buildin support contexts 
* `irails test`          --run project tests 

## Take a look configure file `general.yaml`
 
``` 
    app:
        appdir:
        - apps
        enabled: null
    root: apps.root

    cors:
        allow_credentials: true
        allow_headers:
            - '*'
        allow_methods:
            - '*'
        allow_origins:
            - '*'
    debug: true
    errors:
        error_404_page: '{ROOT.public_dir}/error_404.html'
        error_500_page: '{ROOT.public_dir}/error_500.html'
    log:
        file: ''
        level: DEBUG
        name: iRails
    public_dir: ./public

    view:
        jinja2:
            block_end_string: '%}'
            block_start_string: '{%'
            comment_end_string: '#}'
            comment_start_string: '{#'
            variable_end_string: '}'
            variable_start_string: ${
        static_format:
        - vue
        - html
    i18n:
        lang: ['zh']
        url_lang_key: 'lang'
```
## Take a look controller file 
 
```python
    from irails import api_router,api,Request,Response,BaseController,application
 
    @api_router(path='/{controller}',auth='none')
    class AdminController(BaseController): 
        @api.get("/index")
        def index(self):
            """
            :title Admin
            """
            return self.view()
```