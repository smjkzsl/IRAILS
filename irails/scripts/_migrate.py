import argparse
import os, sys
import uvicorn
from irails.config import IS_IN_irails
from irails._loader import _load_apps
 
from irails.config import config

def main():
     
    if not IS_IN_irails:
        print(f"`migrate` command must run in the directory of irails project")
        exit()
    self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
    parser = argparse.ArgumentParser(usage=f"{sys.argv[0]} {self_file} [-u --upgrade] [-d --downgrade]", description='database migration') 
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-u','--upgrade',action='store_true', help="upgrade database")    
    group.add_argument('-d','--downgrade',action='store_true', help="downgrade database")    
    
    args = parser.parse_args()
     
    if args.upgrade:
        is_up = True
    elif args.downgrade:
        is_up = False
    else:
        parser.print_usage()
        exit()
    from irails.database import check_migration,init_database
    db_cfg = config.get("database")
    db_uri = db_cfg.get("uri")
    alembic_ini = db_cfg.get('alembic_ini')
    _load_apps()
    engine = init_database(db_uri,debug=True,cfg = db_cfg)
    if engine:
        check_migration(engine=engine,uri= db_uri,alembic_ini= alembic_ini,upgrade=is_up)


       