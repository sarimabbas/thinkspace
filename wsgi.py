from app import create_app
from config import productionConfig
app = create_app(productionConfig)

if __name__ == '__main__':
    app.run()
