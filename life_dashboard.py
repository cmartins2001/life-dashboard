import marimo

__generated_with = "0.16.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import altair as alt
    return duckdb, mo


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
def _(trans_df):
    cat = 'Car'
    cat_df = (
        trans_df
            .loc[trans_df['category']==cat]
        .groupby(['date_year', 'date_month', 'category'], as_index=False)
        .agg(
            amount=('amount', 'sum')
        )
        .astype({'date_year' : 'category'})
    )
    cat_df
    return


@app.cell
def _():
    # spend_chart = (
    #     alt.Chart(cat_df)
    #     .mark_line()
    #     .encode(
    #         x=alt.X(field='date_month:O'),
    #         y=alt.Y(field='amount:Q', aggregate='sum'),
    #         color=alt.Color(field='date_year', type='nominal'),
    #     )
    #     # .properties(
    #     #     title=f'{cat} Net Spend Over Time',
    #     #     height=290,
    #     #     width='container',
    #     #     config={
    #     #         'axis': {
    #     #             'grid': False
    #     #         }
    #     #     }
    #     # )
    # )
    # spend_chart
    return


if __name__ == "__main__":
    app.run()
