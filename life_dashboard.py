import marimo

__generated_with = "0.18.4"
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
def _(mo):
    mo.md(r"""
    ### Connect to the DuckDB Database
    """)
    return


@app.cell
def _(duckdb):
    # DB CONNECTION:
    # DATABASE_URL = "C:/Users/cmart/Documents/GitHub/life-dashboard/connor_personal.duckdb"
    DATABASE_URL = "C:/Users/cmart/databases/connor_personal.duckdb"
    engine = duckdb.connect(DATABASE_URL, read_only=True)
    return (engine,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Read Daily Log Data
    """)
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
    return (daily_log_df,)


@app.cell
def _(alt, daily_log_df, mo, pd):
    ### WEEKLY log metrics:
    weekly_log = (
        daily_log_df

            # Use ISO week and year to avoid confusion with end dates:
        .astype({'date_year':'str', 'date_month':'str'})
        .assign(
            iso_yr=lambda x:pd.to_datetime(x.date).dt.isocalendar().year,
            iso_week=lambda x: pd.to_datetime(x.date).dt.isocalendar().week
        
        )
        .groupby(['iso_yr', 'iso_week'], as_index=False, observed=True)
        .agg(
            avg_rating=('rating', 'mean'),
            workout_count=('workout_bool', 'sum')
        )
    )

    # plot weekly avg. rating:
    weekly_avg_rating_chart = (
        alt.Chart(weekly_log)
        .mark_line()
        .encode(
            x=alt.X(field='iso_week', type='nominal'),
            y=alt.Y(field='avg_rating', type='quantitative', aggregate='mean'),
            color=alt.Color(field='iso_yr', type='nominal'),
            tooltip=[
                alt.Tooltip(field='iso_week'),
                alt.Tooltip(field='avg_rating', aggregate='mean', format=',.2f'),
                alt.Tooltip(field='iso_yr')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )

    # plot weekly workout count:
    weekly_workout_count_chart = (
        alt.Chart(weekly_log)
        .mark_line()
        .encode(
            x=alt.X(field='iso_week', type='nominal'),
            y=alt.Y(field='workout_count', type='quantitative', aggregate='sum'),
            color=alt.Color(field='iso_yr', type='nominal'),
            xOffset='iso_yr',
            tooltip=[
                alt.Tooltip(field='iso_week'),
                alt.Tooltip(field='workout_count', aggregate='sum', format=',.2f'),
                alt.Tooltip(field='iso_yr')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )

    # Save charts to a display list:
    weekly_trends = mo.vstack([
        weekly_avg_rating_chart,
        weekly_workout_count_chart
    ])
    return (weekly_trends,)


@app.cell
def _(mo, monthly_log):
    ### CURRENT vs. average monthly workout count metric:
    current_month_workout_count = (
        monthly_log.loc[monthly_log['year_month']=='2025-12']
        ['workout_count'].sum()
    )

    prior_months_workout_count = (
        monthly_log.loc[monthly_log['year_month']<='2025-12']
        ['workout_count'].median()
    )

    wrkt_diff = current_month_workout_count - prior_months_workout_count
    if wrkt_diff < 0:
        _diff = 'decrease'
    elif wrkt_diff > 0:
        _diff = 'increase'

    mo.stat(
        label="Current Monthly Workout Count:",
        value=f'{current_month_workout_count:}',
        caption=f'from YTD Median of {prior_months_workout_count:.1f}',
        direction=_diff
    )
    return


@app.cell
def _(alt, daily_log_df, mo, pd):
    ### MONTHLY log metrics:
    monthly_log = (
        daily_log_df
        .astype({'date_year':'str', 'date_month':'str'})
        .assign(
            date_month_nm=lambda df_: pd.to_datetime(df_['date']).dt.strftime("%m"),
            year_month=lambda df_: pd.to_datetime(df_['date']).dt.strftime("%Y-%m"),
        )
        .groupby(['date_year', 'year_month', 'date_month_nm', 'date_month'], as_index=False, observed=True)
        .agg(
            avg_rating=('rating', 'mean'),
            workout_count=('workout_bool', 'sum')
        )
    )

    # plot monthly avg. rating:
    avg_rating_chart = (
        alt.Chart(monthly_log)
        .mark_line()
        .encode(
            x=alt.X(field='date_month_nm', type='nominal'),
            y=alt.Y(field='avg_rating', type='quantitative', aggregate='mean'),
            color=alt.Color(field='date_year', type='nominal'),
            tooltip=[
                alt.Tooltip(field='date_month_nm'),
                alt.Tooltip(field='avg_rating', aggregate='mean', format=',.2f'),
                alt.Tooltip(field='date_year')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )

    # plot monthly workout count:
    workout_count_chart = (
        alt.Chart(monthly_log)
        .mark_line()
        .encode(
            x=alt.X(field='date_month_nm', type='nominal'),
            y=alt.Y(field='workout_count', type='quantitative', aggregate='sum'),
            color=alt.Color(field='date_year', type='nominal'),
            xOffset='date_year',
            tooltip=[
                alt.Tooltip(field='date_month_nm'),
                alt.Tooltip(field='workout_count', aggregate='sum', format=',.2f'),
                alt.Tooltip(field='date_year')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )

    # Save charts to a display list:
    monthly_trends = mo.vstack([
        avg_rating_chart,
        workout_count_chart
    ])
    return monthly_log, monthly_trends


@app.cell
def _(mo, monthly_trends, weekly_trends):
    # Use marimo tab to choose which trend charts to show:
    mo.ui.tabs({"Weekly Trends": weekly_trends, "Monthly Trends": monthly_trends})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Load Transactions Data
    """)
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
    mo.md(r"""
    ### Monthly and Weekly Essential vs. Non-Essential Spend Trend
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Monthly Spend by Category:
    """)
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
    mo.md(r"""
    ### This Week's Spending Stats:
    """)
    return


@app.cell
def _(date, trans_modified):
    # Define relevant variables:
    current_yr = date.today().year
    current_month = date.today().month
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
    return before_this_week, this_week


@app.cell
def _(before_this_week, mo, this_week):
    ### DISPLAY CURRENT WEEK SPENDING VS. AVG. WEEK METRICS:

    def week_comparison_metric(curr_week_df, prior_weeks_df, essentials_tag : str, label : str):
    
        # calc current week total:
        curr_wk_sum = curr_week_df.loc[curr_week_df['essential_ind']==essentials_tag]['amount'].sum()
    
        # calc avg. weekly total of all prior weeks:
        prior_wks_sum = (
            prior_weeks_df
            .loc[prior_weeks_df['essential_ind']==essentials_tag]
            .groupby('week', as_index=False)
            .agg({'amount' : 'sum'})
                ['amount'].median()
        )

        # determine direction of difference:
        beat_miss = curr_wk_sum - prior_wks_sum
        if beat_miss < 0:
            diff = 'Down'
        elif beat_miss > 0:
            diff = 'Up'
        else:
            diff = 'No Different'

        return mo.stat(
            label=label,
            value=f'${curr_wk_sum:.2f}',
            caption=f'{diff} from YTD Median of ${prior_wks_sum:.2f}'
        )


    # clean_labels = ["This Week's NON-Essentials Spend:", "This Week's Essentials Spend:"]
    ess_tags = ["Non-Essential", "Essential"]
    essential_compare_stats = [week_comparison_metric(
        this_week,
        before_this_week,
        essentials_tag=tag,
        label=f"This Week's {tag} Spend:"
    ) for tag in ess_tags]

    # display the metrics in marimo:
    mo.hstack(essential_compare_stats)
    return


if __name__ == "__main__":
    app.run()
