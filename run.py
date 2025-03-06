from api.endpoints import app as api_app
from storefront.views import app as store_app

if __name__ == '__main__':
    api_app.run(debug=True)
    store_app.run(debug=True)
