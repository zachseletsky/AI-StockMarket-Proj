from plotly import express
import pandas as pd
import os


equities_path = "data-lake/raw/equities"
graph_output_path = "data-lake/processed/graphs/"
def graph_equity():
  folders = os.listdir(equities_path)
  print("Available Folders: ")
  for folder in folders:
    print(folder)

  folder = input("Enter folder name: ")
  fPath = equities_path + "/" + folder
  files = os.listdir(fPath)
  print("Available files: ")
  count = 0
  for f in files:
    print(f"{count}. {f}")
    count += 1
  target = int(input("Enter number of file you wish to graph: "))
  dataframe = pd.read_csv(fPath + "/" + files[target])
  dataframe = dataframe.drop(index=[0,1,2])
  dataframe.columns = ["date", "close", "high", "low", "open", "volume"]
  y_cols = dataframe.columns[1:]
  high = dataframe[y_cols].max().max()
  low = dataframe[y_cols].min().min()

  for i in range(1,len(dataframe.columns)):
    col = dataframe.columns[i]
    dataframe[col] = dataframe[col].round(2)
  
  figure = express.line(dataframe, x=dataframe.columns[0], y=dataframe.columns[1:], title="MSFT")
  figure.update_yaxes(type="linear", range=[high,low])
  figure.write_html(graph_output_path + files[target] + ".html")


if __name__ == "__main__":
  graph_equity()