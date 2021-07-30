from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from Model_MySQL import db
from run import create_server
app = create_server('config')
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
if __name__=="__main__":
    manager.run()