import marimo

__generated_with = "0.16.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    return duckdb, mo


@app.cell
def _(duckdb):
    # DB CONNECTION:
    DATABASE_URL = "C:/Users/cmart/Documents/GitHub/life-dashboard/connor_personal.duckdb"
    engine = duckdb.connect(DATABASE_URL, read_only=True)
    return (engine,)


@app.cell
def _(daily_log, engine, mo):
    _df = mo.sql(
        f"""
        SELECT *
        	,YEAR(date) AS date_year
            ,MONTH(date) AS date_month
        FROM daily_log
        """,
        engine=engine
    )
    return


if __name__ == "__main__":
    app.run()
