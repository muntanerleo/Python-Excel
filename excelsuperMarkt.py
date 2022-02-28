import pandas as pd
import plotly.express as px
import streamlit as st

# setting up the webpage content
# emojis taken from: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Sales Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide"
)

# load the data from the excel sheet and make it into a dataframe
@st.cache
def get_data_from_excel():
  data_frame = pd.read_excel(
  # code below: gets the file name from the directory
  io = 'supermarkt_sales.xlsx',
  
  # code below: opens the xlsx file(make sure you have the openpyxl library installed in the local enviorment).
  engine = 'openpyxl',
  
  # code below: looks at the sheet in the excel file
  sheet_name = 'Sales',
  
  # code below: skips rows
  skiprows = 3,
  
  # code below: specifies which rows i want to use 
  usecols = 'B:R',
  
  # code below: how many rows i included in my selection
  nrows = 1000,
  )
  # code below: print out the dataframe content onto the terminal to check if the code worked.
  # print(dataframe)

  # Add 'hour' column to the dataframe. remeber to use the pd.to_datetime() method-
  # because the hour object is a string 
  data_frame["hour"] = pd.to_datetime(data_frame["Time"], format="%H:%M:%S").dt.hour
  return data_frame

data_frame = get_data_from_excel()


# --SideBar--
st.sidebar.header("Filter Data Here:")

city = st.sidebar.multiselect(
  "Select the City:",
 
  # code below: allows the user to choose cities from the excel sheet
  options=data_frame["City"].unique(),
  default=data_frame["City"].unique()
)

# code below: displays all the different customer types 
customer_type = st.sidebar.multiselect(
  "Select the Customer Type:",
 
  # code below: allows the user to choose Customer type from the excel sheet
  options=data_frame["Customer_type"].unique(),
  default=data_frame["Customer_type"].unique()
)

# code below: displays the gender
gender = st.sidebar.multiselect(
  "Select the Gender:",
 
  # code below: allows the user to choose gender from the excel sheet
  options=data_frame["Gender"].unique(),
  default=data_frame["Gender"].unique()
) 

# for each of the fields above, streamlit returns a list with the selected options.
# those lists are stored in my variables city, customer_type, gender
# to filter the dataframe i will be using the query() method
# this stores my dataframe 

# now i store the filtered dataframe in the variable df_selection
df_selection = data_frame.query(
  # now i can query my columns based on the selection
  # pandas will filter the city column based on the city list
  # use the @ to refer to the variable
  "City == @city & Customer_type == @customer_type & Gender == @gender"
)

# --Main Page--
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

# Top KPI's
# i will display the total sales, the average rating, and average sale by transaction

# the total sales will be the sum of the Total column. this will return a float number 
# but i will convert it into an integer
total_sales = int(df_selection["Total"].sum())

# for the average rating i take the mean from the rating column and round it with 1 decimal
average_rating = round(df_selection["Rating"].mean(), 1)

# next to the average rating i will illustrate the rating score by emojis
# i also need to convert this into am int 
star_rating = ":star:" * int(round(average_rating, 0))

# the last thing is calculating the average sale of a transaction.
# i will apply the mean to the total column 
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

# now i will display these in three separate columns by using .column() method
left_column, middle_column, right_column = st.columns(3)

# now i can insert the content into the columns
# left column will display total sales
with left_column:
  st.subheader("Total Sales:")
  st.subheader(f"US $ {total_sales:,}")

# middle column will show info on the rating 
with middle_column:
  st.subheader("Average Rating:")
  st.subheader(f"{average_rating} {star_rating}")
  
# right column will display the average sales by transaction
with right_column:
  st.subheader("Average Sales Per Transaction:")
  st.subheader(f"US $ {average_sale_by_transaction}")
  
# to separate these KPIs from the next section i will insert a markdow 
st.markdown("---")

# Sales By Product Line (Bar Chart)
sales_by_product_line = (
  df_selection.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
)

# now i will store the bar chart in a variable and use a plotly library to plot the data
fig_product_sales = px.bar(
  sales_by_product_line,
  x="Total",
  y=sales_by_product_line.index,
  orientation="h",
  title="<b>Sales by Product Line</b>",
  color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
  template="plotly_white",
)

# i will remove the grid lines and the backgroud color from the barchart
fig_product_sales.update_layout(
  plot_bgcolor="rgba(0,0,0,0)",
  xaxis=(dict(showgrid=False))
)

# Sales By Hour [Bar Chart]
# group the sales by hour 
sales_by_hour = df_selection.groupby(by=["hour"]).sum()[["Total"]]

# make the bar chart
fig_hourly_sales = px.bar(
  sales_by_hour,
  x=sales_by_hour.index,
  y="Total",
  title="<b>Sales by Hour</b>",
  color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
  template="plotly_white",
)

fig_hourly_sales.update_layout(
  xaxis=dict(tickmode="linear"),
  plot_bgcolor="rgba(0,0,0,0)",
  yaxis=(dict(showgrid=False)),
)

# putting the charts next to each other
left_column, right_column = st.columns(2)

# left column i will display the hourly sales
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)

# right column will display the product sales
right_column.plotly_chart(fig_product_sales, use_container_width=True)