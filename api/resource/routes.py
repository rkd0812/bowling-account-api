from api.resource.account import AccountApi,AccountsApi,AccountRegisterApi, AccountAuthApi

def init_routes(api):
    api.add_resource(AccountApi, '/account/<string:user_id>')
    api.add_resource(AccountsApi, '/accounts')
    api.add_resource(AccountRegisterApi, '/account')
    api.add_resource(AccountAuthApi, '/accountMailAuth')