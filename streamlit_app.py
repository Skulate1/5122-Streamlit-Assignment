import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Data App Assignment, on July 14th")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)
st.write(df.index.dtype)
st.write(sales_by_month.head())

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='ME')).sum()
st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## Your additions")

# (1) add a drop down for Category 
category = st.selectbox(
    "Select a Category",
    sorted(df["Category"].unique())
)

# (2) add a multi-select for Sub_Category *in the selected Category (1)
# Filter the sub-category options down to only those inside the chosen category
sub_category_options = sorted(
    df.loc[df["Category"] == category, "Sub_Category"].unique()
)

sub_categories = st.multiselect(
    "Select one or more Sub-Categories",
    sub_category_options
)

if not sub_categories:
    st.info("Pick at least one Sub-Category above to see the chart and the metrics.")
else:
    # Rows matching both the selected category and the selected sub-categories
    filtered = df[
        (df["Category"] == category) & (df["Sub_Category"].isin(sub_categories))
    ]

    # (3) show a line chart of sales for the selected items in (2)
    # Order_Date is already the index, so Grouper can resample it by month
    filtered_sales_by_month = filtered.filter(items=["Sales"]).groupby(pd.Grouper(freq="ME")).sum()
     
    st.write("### Monthly sales for the selected Sub-Categories")
    st.line_chart(filtered_sales_by_month, y="Sales")

    # (4) show three metrics
    # Three metrics: total sales, total profit, overall profit margin
    total_sales = filtered["Sales"].sum()
    total_profit = filtered["Profit"].sum()
    profit_margin = (total_profit / total_sales * 100) if total_sales else 0

    # (5) use the delta option in the overall profit margin metric to show the difference between the overall average profit margin (all products across all categories)
    # delta - how the selection's margin compares to the margin of every product across every category
    overall_profit_margin = df["Profit"].sum() / df["Sales"].sum() * 100
    margin_delta = profit_margin - overall_profit_margin
    
    st.write("### Metrics for the selected Sub-Categories")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric(
        "Overall Profit Margin",
        f"{profit_margin:.2f}%",
        delta=f"{margin_delta:.2f}%",
    )
    st.caption(
        f"Delta compares against the overall average profit margin of "
        f"{overall_profit_margin:.2f}% across all products in all categories."
)
