from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from model.models import *
# from model.product_tables import *
from view.app import App

if __name__ == '__main__':
    engine = create_engine('sqlite:///data/data.db')
    session = Session(bind=engine)
    Base.metadata.create_all(bind=engine)
    app = App(session)
    app.mainloop()