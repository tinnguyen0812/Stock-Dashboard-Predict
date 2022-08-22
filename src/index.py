from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
from pages import portfolio, watchlist, home, search
from app import app

nav_item = dbc.NavItem(dbc.NavLink("Home", href="/home"))

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Search", href="/search"),
        dbc.DropdownMenuItem("Watchlist", href="/watchlist"),
        dbc.DropdownMenuItem("Portfolio", href="/portfolio")
    ],
    nav=True,
    in_navbar=True,
    label="Explore",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("STOCK PREDICT AND STORE"),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [nav_item, dropdown], className="ms-auto", navbar=True
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ]
    ),
    className="mb-5"
)


def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


app.callback(
    Output(f"navbar-collapse", "is_open"),
    [Input(f"navbar-toggler", "n_clicks")],
    [State(f"navbar-collapse", "is_open")],
)(toggle_navbar_collapse)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])

def displayPage(newpath):
    if newpath == '/portfolio':
        return portfolio.layout

    elif newpath == '/watchlist':
        return watchlist.layout

    elif newpath == '/search':
        return search.layout
        
    else:
        return home.layout

