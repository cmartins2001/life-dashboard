import marimo

__generated_with = "0.16.2"
app = marimo.App(
    width="medium",
    layout_file="layouts/life_dashboard.grid.json",
)


@app.cell
def _():
    import marimo as mo
    import duckdb
    import pandas as pd
    import altair as alt
    import numpy as np
    import datetime as datetime
    from datetime import datetime, date, timedelta
    return alt, date, duckdb, mo, np, pd


@app.cell
def _(duckdb):
    # DB CONNECTION:
    # DATABASE_URL = "C:/Users/cmart/Documents/GitHub/life-dashboard/connor_personal.duckdb"
    DATABASE_URL = "C:/Users/cmart/databases/connor_personal.duckdb"
    engine = duckdb.connect(DATABASE_URL, read_only=True)
    return (engine,)


@app.cell
def _(engine, mo, transactions):
    _df = mo.sql(
        f"""
        SELECT * FROM transactions LIMIT 100
        """,
        engine=engine
    )
    return


@app.cell
def _(daily_log, engine, mo):
    daily_log_df = mo.sql(
        f"""
        SELECT *
        	,YEAR(date) AS date_year
            ,MONTH(date) AS date_month
        FROM daily_log
        """,
        engine=engine
    )
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Load Transactions Data""")
    return


@app.cell
def _(engine, mo, transactions):
    trans_df = mo.sql(
        f"""
        SELECT *
            ,MONTH(date) AS date_month
            ,YEAR(date) AS date_year
        FROM transactions
        WHERE date_year >= 2024
        """,
        engine=engine
    )
    return (trans_df,)


@app.cell
def _(np, pd, trans_df):
    # Define "essentials category":

    trans_modified = (
        trans_df.loc[(~trans_df['name'].str.contains('Mobile Banking Payment'))]
        .assign(
            essential_ind=lambda x: np.where(x.category.isin([
                'Car', 'Healthcare', 'Education', 'Transit'
            ]), 'Essential', 'Non-Essential'),
            date=lambda x: pd.to_datetime(x.date).dt.strftime("%Y-%m-%d"),
            week=lambda x: pd.to_datetime(x.date).dt.isocalendar().week
        )
        .query("amount>=0")
    )

    trans_modified.groupby(['date_year', 'date_month', 'essential_ind'], as_index=False)['amount'].sum()
    return (trans_modified,)


@app.cell
def _(mo):
    mo.md(r"""### Monthly Spend by Category:""")
    return


@app.cell
def _(mo, trans_modified):
    # Pick a category to plot over time:
    category = mo.ui.dropdown(
        label='Pick a spend category:',
        options=[_ for _ in trans_modified['category'].unique()],
        value='Car'
    )

    # Pick a plotting freq:
    plot_freq = mo.ui.dropdown(
        label='Pick a plotting frequency:',
        options=['week', 'date_month'],
        value='week'
    )
    mo.hstack([category, plot_freq])
    return category, plot_freq


@app.cell
def _(category, plot_freq, trans_modified):
    # Monthly spend by 
    cat_df = (
        trans_modified
            .loc[
            (trans_modified['category']==category.value)
            ]
        .groupby(['date_year', plot_freq.value, 'category'], as_index=False, observed=False)
        .agg(
            amount=('amount', 'sum')
        )
        .astype({'date_year' : 'category', f'{plot_freq.value}' : 'category'})
    )
    cat_df
    return (cat_df,)


@app.cell
def _(alt, cat_df, category, plot_freq):
    spend_chart = (
        alt.Chart(cat_df)
        .mark_bar()
        .encode(
            x=alt.X(field=f'{plot_freq.value}'),
            y=alt.Y(field='amount', aggregate='sum'),
            xOffset='date_year',
            # color=alt.Color(field='date_year', type='nominal'),
            color=alt.Color(field='date_year', type='nominal', scale={
                'scheme': 'dark2'
            }),
            tooltip=[
                alt.Tooltip(field=plot_freq.value),
                alt.Tooltip(field='amount', aggregate='sum', format=',.2f'),
                alt.Tooltip(field='date_year')
            ]
        )
        .properties(
            title=f'{category.value} Net Spend Over Time',
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )
    spend_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### This Week's Spending Stats:""")
    return


@app.cell
def _(date, mo, trans_modified):
    # Define relevant variables:
    current_yr = date.today().year
    current_week = date.today().isocalendar().week

    # Get transactions from current week:
    this_week = (
        trans_modified
        .loc[
            (trans_modified['date_year'] == current_yr)
            & (trans_modified['week'] == current_week)
        ]
    )

    # Get any transactions before this week in the current year:
    before_this_week = (
        trans_modified
        .loc[
            (trans_modified['date_year'] == current_yr)
            & (trans_modified['week'] < current_week)
        ]
    )

    # ESSENTIALS weeekly spend metric:
    curr_essentials_spend = (
        this_week
        .loc[this_week['essential_ind']=='Essential']
        ['amount'].sum()
    )

    avg_essentials_spend = (
        before_this_week
        .loc[before_this_week['essential_ind']=='Essential']
        .groupby('week', as_index=False)
        .agg({'amount' : 'sum'})
        ['amount'].median()
    )

    ess_beat_miss = curr_essentials_spend - avg_essentials_spend
    if ess_beat_miss < 0:
        _diff = 'Down'
    elif ess_beat_miss > 0:
        _diff = 'Up'
    else:
        _diff = 'No Different'

    mo.stat(
        label="This Week's Essentials Spend:",
        value=f'${curr_essentials_spend:.2f}',
        caption=f'{_diff} from YTD Median of ${avg_essentials_spend:.2f}'
    
    )
    return before_this_week, this_week


@app.cell
def _(before_this_week, mo, this_week):
    curr_nonessentials_spend = (
        this_week
        .loc[this_week['essential_ind']!='Essential']
        ['amount'].sum()
    )

    avg_nonessentials_spend = (
        before_this_week
        .loc[before_this_week['essential_ind']!='Essential']
        .groupby('week', as_index=False)
        .agg({'amount' : 'sum'})
        ['amount'].median()
    )

    noness_beat_miss = curr_nonessentials_spend - avg_nonessentials_spend
    if noness_beat_miss < 0:
        _diff = 'Down'
    elif noness_beat_miss > 0:
        _diff = 'Up'
    else:
        _diff = 'No Different'

    mo.stat(
        label="This Week's NON-Essentials Spend:",
        value=f'${curr_nonessentials_spend:.2f}',
        caption=f'{_diff} from YTD Median of ${avg_nonessentials_spend:.2f}'
    
    )
    return


if __name__ == "__main__":
    app.run()
