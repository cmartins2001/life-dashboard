import marimo

__generated_with = "0.16.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    return duckdb, mo


@app.cell
def _():
    # testing local DuckDB connection:
    # conn = duckdb.connect("questionnaire.duckdb", read_only=True)
    # df = conn.execute("SELECT * FROM entries ORDER BY date").fetchdf()
    # conn.close()
    # df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return


@app.cell
def _(duckdb):
    # DB CONNECTION:
    DATABASE_URL = "C:/Users/cmart/Documents/GitHub/life-dashboard/connor_personal.duckdb"
    engine = duckdb.connect(DATABASE_URL, read_only=True)
    return (engine,)


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        -- SELECT * FROM daily_log LIMIT 100
        """,
        engine=engine
    )
    return


if __name__ == "__main__":
    app.run()
