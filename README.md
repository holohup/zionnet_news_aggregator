# zionnet_news_aggregator
News Aggregator build with microservices


all logs are mapped outside containers
settings: max number of sentences: int, interests: comma-separated str, is_admin: bool, max_news: int

admin can: get full user info, delete user, change password

is_admin non volatile, settings volatile

known issues.
at startup the services can give a server error without explanation. This happens because in my pursuit of a single source of truth, I get settings common for various modules from DAPR, which is not yet working (since the service containers run before dapr sidecars), and I do not try to catch the exception since proper logging is not initialized yet

the solution utilizes http, which is not secure

every service has an access to secrets, they use only what is needed, but potentially could request secrets that do not concern them

!NB att to promt if there're duplicates in summary+title, choose the most interesting id