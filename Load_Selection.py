{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyO69dAYauCdmgYPWDvCth1Q",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/TeneikaAskew/logistics/blob/main/Load_Selection.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "from google.colab import auth\n",
        "auth.authenticate_user()\n",
        "\n",
        "import gspread\n",
        "from google.auth import default\n",
        "import pandas as pd\n",
        "from datetime import datetime, timedelta\n",
        "\n",
        "# Use the default credentials\n",
        "creds, _ = default()\n",
        "gc = gspread.authorize(creds)\n",
        "\n",
        "# Now access your Google Sheets\n",
        "spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1aFmYrACUYVfIdoaQ-YYd3Bx5aZ9cDQk-kRmukSTpmJI'\n",
        "workbook = gc.open_by_url(spreadsheet_url)\n",
        "worksheet = workbook.worksheet('Emails')\n",
        "rows = worksheet.get_all_records()"
      ],
      "metadata": {
        "id": "EouLPE09wgFF"
      },
      "execution_count": 52,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "import numpy as np\n",
        "# Convert to a DataFrame and clean data\n",
        "df = pd.DataFrame(rows)\n",
        "df.columns = ['Deadhead Mileage','Load #', 'Carrier Pay', 'Miles', 'RPM', 'Origin', 'Destination', 'PU Date', 'DO Date', 'Commodity', 'Trailer Type']\n",
        "df['PU Date'] = pd.to_datetime(df['PU Date'], errors='coerce')\n",
        "df['DO Date'] = pd.to_datetime(df['DO Date'], errors='coerce')\n",
        "df['Miles'] = pd.to_numeric(df['Miles'], errors='coerce')\n",
        "df['Carrier Pay'] = df['Carrier Pay'].replace('[\\$,]', '', regex=True).astype(float)\n",
        "df['End Time'] = df['DO Date'] + timedelta(hours=10)\n",
        "\n",
        "# Function to estimate travel time\n",
        "def estimate_travel_time(miles):\n",
        "    return timedelta(hours=miles / 60)\n",
        "\n",
        "# Calculate distance to origin for each load\n",
        "start_location = \"3200 W 5th St, Lumberton, NC, 28358\"\n",
        "\n",
        "# Sort loads by Carrier Pay first, then by Mileage to Origin\n",
        "df_sorted = df.sort_values(by=['Carrier Pay', 'Deadhead Mileage'], ascending=[False, True])\n",
        "\n",
        "# Find feasible next loads based on operational constraints\n",
        "def find_feasible_loads(current_load, all_loads, start_time):\n",
        "    feasible_loads = []\n",
        "    current_end_time = max(current_load['End Time'], start_time)\n",
        "    for _, next_load in all_loads.iterrows():\n",
        "        travel_time = estimate_travel_time(current_load['Miles'])\n",
        "        if next_load['PU Date'] >= current_end_time + travel_time:\n",
        "            feasible_loads.append(next_load['Load #'])\n",
        "        if len(feasible_loads) >= 3:\n",
        "            break\n",
        "    return feasible_loads\n",
        "\n",
        "# Collect follow-up load data\n",
        "load_follow_ups = []\n",
        "for _, load in df_sorted.iterrows():\n",
        "    next_loads = find_feasible_loads(load, df_sorted, datetime(2024, 5, 10, 7, 0))\n",
        "    load_data = {\n",
        "        'Deadhead Mileage': load['Deadhead Mileage'],\n",
        "        'Load #': load['Load #'],\n",
        "    }\n",
        "    for idx, next_load in enumerate(next_loads, start=1):\n",
        "        load_data[f'Next Load {idx}'] = next_load\n",
        "\n",
        "    load_follow_ups.append(load_data)\n",
        "\n",
        "# # Convert to DataFrame and display\n",
        "# follow_up_df = pd.DataFrame(load_follow_ups)\n",
        "# print(follow_up_df.head())  # Display the top entries\n",
        "# follow_up_df\n",
        "\n",
        "# Sort loads by Carrier Pay first, then by Deadhead Mileage\n",
        "df_sorted = df.sort_values(by=['Carrier Pay', 'Deadhead Mileage'], ascending=[False, True])\n",
        "\n",
        "# Create a DataFrame containing the desired columns for all loads\n",
        "all_loads_df = pd.DataFrame({\n",
        "    'Deadhead Mileage': df_sorted['Deadhead Mileage'],\n",
        "    'Load #': df_sorted['Load #'],\n",
        "    'Trailer Type': df_sorted['Trailer Type'],\n",
        "    'Origin': df_sorted['Origin'],\n",
        "    'Destination': df_sorted['Destination'],\n",
        "    'Carrier Pay': df_sorted['Carrier Pay']\n",
        "})\n",
        "\n",
        "#print(all_loads_df)\n",
        "all_loads_df"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/",
          "height": 579
        },
        "id": "_BnjndXR_Ef4",
        "outputId": "3c6380b8-146e-43a2-e263-fba17c22f0af"
      },
      "execution_count": 63,
      "outputs": [
        {
          "output_type": "execute_result",
          "data": {
            "text/plain": [
              "    Deadhead Mileage     Load # Trailer Type  \\\n",
              "58             177.0  137727111    53VN, VAN   \n",
              "47             191.0  137718030     FLAT, SD   \n",
              "68             191.0  137728967     FLAT, SD   \n",
              "41             191.0  137716665     FLAT, SD   \n",
              "43             191.0  137717716     FLAT, SD   \n",
              "..               ...        ...          ...   \n",
              "71             212.0  137730859   FLAT, STEP   \n",
              "76             212.0  137735040   FLAT, STEP   \n",
              "78             212.0  137735554         FLHS   \n",
              "81             212.0  137737320   FLAT, STEP   \n",
              "82             212.0  137737354         FLHS   \n",
              "\n",
              "                              Origin                       Destination  \\\n",
              "58  NORTH CHARLESTON, SOUTH CAROLINA  NORTH CHARLESTON, SOUTH CAROLINA   \n",
              "47         ALLENDALE, SOUTH CAROLINA               HINESVILLE, GEORGIA   \n",
              "68         ALLENDALE, SOUTH CAROLINA               HINESVILLE, GEORGIA   \n",
              "41           FAIRFAX, SOUTH CAROLINA           LANDRUM, SOUTH CAROLINA   \n",
              "43           FAIRFAX, SOUTH CAROLINA           LANDRUM, SOUTH CAROLINA   \n",
              "..                               ...                               ...   \n",
              "71      FOUNTAIN INN, SOUTH CAROLINA        PROSPERITY, SOUTH CAROLINA   \n",
              "76      FOUNTAIN INN, SOUTH CAROLINA        PROSPERITY, SOUTH CAROLINA   \n",
              "78      FOUNTAIN INN, SOUTH CAROLINA        PROSPERITY, SOUTH CAROLINA   \n",
              "81      FOUNTAIN INN, SOUTH CAROLINA        PROSPERITY, SOUTH CAROLINA   \n",
              "82      FOUNTAIN INN, SOUTH CAROLINA        PROSPERITY, SOUTH CAROLINA   \n",
              "\n",
              "    Carrier Pay  \n",
              "58      2700.00  \n",
              "47      1248.06  \n",
              "68      1248.06  \n",
              "41      1248.00  \n",
              "43      1248.00  \n",
              "..          ...  \n",
              "71       312.00  \n",
              "76       312.00  \n",
              "78       312.00  \n",
              "81       312.00  \n",
              "82       312.00  \n",
              "\n",
              "[100 rows x 6 columns]"
            ],
            "text/html": [
              "\n",
              "  <div id=\"df-3789984c-de4f-4754-a0ee-4e74263c5b10\" class=\"colab-df-container\">\n",
              "    <div>\n",
              "<style scoped>\n",
              "    .dataframe tbody tr th:only-of-type {\n",
              "        vertical-align: middle;\n",
              "    }\n",
              "\n",
              "    .dataframe tbody tr th {\n",
              "        vertical-align: top;\n",
              "    }\n",
              "\n",
              "    .dataframe thead th {\n",
              "        text-align: right;\n",
              "    }\n",
              "</style>\n",
              "<table border=\"1\" class=\"dataframe\">\n",
              "  <thead>\n",
              "    <tr style=\"text-align: right;\">\n",
              "      <th></th>\n",
              "      <th>Deadhead Mileage</th>\n",
              "      <th>Load #</th>\n",
              "      <th>Trailer Type</th>\n",
              "      <th>Origin</th>\n",
              "      <th>Destination</th>\n",
              "      <th>Carrier Pay</th>\n",
              "    </tr>\n",
              "  </thead>\n",
              "  <tbody>\n",
              "    <tr>\n",
              "      <th>58</th>\n",
              "      <td>177.0</td>\n",
              "      <td>137727111</td>\n",
              "      <td>53VN, VAN</td>\n",
              "      <td>NORTH CHARLESTON, SOUTH CAROLINA</td>\n",
              "      <td>NORTH CHARLESTON, SOUTH CAROLINA</td>\n",
              "      <td>2700.00</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>47</th>\n",
              "      <td>191.0</td>\n",
              "      <td>137718030</td>\n",
              "      <td>FLAT, SD</td>\n",
              "      <td>ALLENDALE, SOUTH CAROLINA</td>\n",
              "      <td>HINESVILLE, GEORGIA</td>\n",
              "      <td>1248.06</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>68</th>\n",
              "      <td>191.0</td>\n",
              "      <td>137728967</td>\n",
              "      <td>FLAT, SD</td>\n",
              "      <td>ALLENDALE, SOUTH CAROLINA</td>\n",
              "      <td>HINESVILLE, GEORGIA</td>\n",
              "      <td>1248.06</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>41</th>\n",
              "      <td>191.0</td>\n",
              "      <td>137716665</td>\n",
              "      <td>FLAT, SD</td>\n",
              "      <td>FAIRFAX, SOUTH CAROLINA</td>\n",
              "      <td>LANDRUM, SOUTH CAROLINA</td>\n",
              "      <td>1248.00</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>43</th>\n",
              "      <td>191.0</td>\n",
              "      <td>137717716</td>\n",
              "      <td>FLAT, SD</td>\n",
              "      <td>FAIRFAX, SOUTH CAROLINA</td>\n",
              "      <td>LANDRUM, SOUTH CAROLINA</td>\n",
              "      <td>1248.00</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>...</th>\n",
              "      <td>...</td>\n",
              "      <td>...</td>\n",
              "      <td>...</td>\n",
              "      <td>...</td>\n",
              "      <td>...</td>\n",
              "      <td>...</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>71</th>\n",
              "      <td>212.0</td>\n",
              "      <td>137730859</td>\n",
              "      <td>FLAT, STEP</td>\n",
              "      <td>FOUNTAIN INN, SOUTH CAROLINA</td>\n",
              "      <td>PROSPERITY, SOUTH CAROLINA</td>\n",
              "      <td>312.00</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>76</th>\n",
              "      <td>212.0</td>\n",
              "      <td>137735040</td>\n",
              "      <td>FLAT, STEP</td>\n",
              "      <td>FOUNTAIN INN, SOUTH CAROLINA</td>\n",
              "      <td>PROSPERITY, SOUTH CAROLINA</td>\n",
              "      <td>312.00</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>78</th>\n",
              "      <td>212.0</td>\n",
              "      <td>137735554</td>\n",
              "      <td>FLHS</td>\n",
              "      <td>FOUNTAIN INN, SOUTH CAROLINA</td>\n",
              "      <td>PROSPERITY, SOUTH CAROLINA</td>\n",
              "      <td>312.00</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>81</th>\n",
              "      <td>212.0</td>\n",
              "      <td>137737320</td>\n",
              "      <td>FLAT, STEP</td>\n",
              "      <td>FOUNTAIN INN, SOUTH CAROLINA</td>\n",
              "      <td>PROSPERITY, SOUTH CAROLINA</td>\n",
              "      <td>312.00</td>\n",
              "    </tr>\n",
              "    <tr>\n",
              "      <th>82</th>\n",
              "      <td>212.0</td>\n",
              "      <td>137737354</td>\n",
              "      <td>FLHS</td>\n",
              "      <td>FOUNTAIN INN, SOUTH CAROLINA</td>\n",
              "      <td>PROSPERITY, SOUTH CAROLINA</td>\n",
              "      <td>312.00</td>\n",
              "    </tr>\n",
              "  </tbody>\n",
              "</table>\n",
              "<p>100 rows × 6 columns</p>\n",
              "</div>\n",
              "    <div class=\"colab-df-buttons\">\n",
              "\n",
              "  <div class=\"colab-df-container\">\n",
              "    <button class=\"colab-df-convert\" onclick=\"convertToInteractive('df-3789984c-de4f-4754-a0ee-4e74263c5b10')\"\n",
              "            title=\"Convert this dataframe to an interactive table.\"\n",
              "            style=\"display:none;\">\n",
              "\n",
              "  <svg xmlns=\"http://www.w3.org/2000/svg\" height=\"24px\" viewBox=\"0 -960 960 960\">\n",
              "    <path d=\"M120-120v-720h720v720H120Zm60-500h600v-160H180v160Zm220 220h160v-160H400v160Zm0 220h160v-160H400v160ZM180-400h160v-160H180v160Zm440 0h160v-160H620v160ZM180-180h160v-160H180v160Zm440 0h160v-160H620v160Z\"/>\n",
              "  </svg>\n",
              "    </button>\n",
              "\n",
              "  <style>\n",
              "    .colab-df-container {\n",
              "      display:flex;\n",
              "      gap: 12px;\n",
              "    }\n",
              "\n",
              "    .colab-df-convert {\n",
              "      background-color: #E8F0FE;\n",
              "      border: none;\n",
              "      border-radius: 50%;\n",
              "      cursor: pointer;\n",
              "      display: none;\n",
              "      fill: #1967D2;\n",
              "      height: 32px;\n",
              "      padding: 0 0 0 0;\n",
              "      width: 32px;\n",
              "    }\n",
              "\n",
              "    .colab-df-convert:hover {\n",
              "      background-color: #E2EBFA;\n",
              "      box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);\n",
              "      fill: #174EA6;\n",
              "    }\n",
              "\n",
              "    .colab-df-buttons div {\n",
              "      margin-bottom: 4px;\n",
              "    }\n",
              "\n",
              "    [theme=dark] .colab-df-convert {\n",
              "      background-color: #3B4455;\n",
              "      fill: #D2E3FC;\n",
              "    }\n",
              "\n",
              "    [theme=dark] .colab-df-convert:hover {\n",
              "      background-color: #434B5C;\n",
              "      box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);\n",
              "      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));\n",
              "      fill: #FFFFFF;\n",
              "    }\n",
              "  </style>\n",
              "\n",
              "    <script>\n",
              "      const buttonEl =\n",
              "        document.querySelector('#df-3789984c-de4f-4754-a0ee-4e74263c5b10 button.colab-df-convert');\n",
              "      buttonEl.style.display =\n",
              "        google.colab.kernel.accessAllowed ? 'block' : 'none';\n",
              "\n",
              "      async function convertToInteractive(key) {\n",
              "        const element = document.querySelector('#df-3789984c-de4f-4754-a0ee-4e74263c5b10');\n",
              "        const dataTable =\n",
              "          await google.colab.kernel.invokeFunction('convertToInteractive',\n",
              "                                                    [key], {});\n",
              "        if (!dataTable) return;\n",
              "\n",
              "        const docLinkHtml = 'Like what you see? Visit the ' +\n",
              "          '<a target=\"_blank\" href=https://colab.research.google.com/notebooks/data_table.ipynb>data table notebook</a>'\n",
              "          + ' to learn more about interactive tables.';\n",
              "        element.innerHTML = '';\n",
              "        dataTable['output_type'] = 'display_data';\n",
              "        await google.colab.output.renderOutput(dataTable, element);\n",
              "        const docLink = document.createElement('div');\n",
              "        docLink.innerHTML = docLinkHtml;\n",
              "        element.appendChild(docLink);\n",
              "      }\n",
              "    </script>\n",
              "  </div>\n",
              "\n",
              "\n",
              "<div id=\"df-01493f9e-575e-4a02-ae0d-290db55c7cc2\">\n",
              "  <button class=\"colab-df-quickchart\" onclick=\"quickchart('df-01493f9e-575e-4a02-ae0d-290db55c7cc2')\"\n",
              "            title=\"Suggest charts\"\n",
              "            style=\"display:none;\">\n",
              "\n",
              "<svg xmlns=\"http://www.w3.org/2000/svg\" height=\"24px\"viewBox=\"0 0 24 24\"\n",
              "     width=\"24px\">\n",
              "    <g>\n",
              "        <path d=\"M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z\"/>\n",
              "    </g>\n",
              "</svg>\n",
              "  </button>\n",
              "\n",
              "<style>\n",
              "  .colab-df-quickchart {\n",
              "      --bg-color: #E8F0FE;\n",
              "      --fill-color: #1967D2;\n",
              "      --hover-bg-color: #E2EBFA;\n",
              "      --hover-fill-color: #174EA6;\n",
              "      --disabled-fill-color: #AAA;\n",
              "      --disabled-bg-color: #DDD;\n",
              "  }\n",
              "\n",
              "  [theme=dark] .colab-df-quickchart {\n",
              "      --bg-color: #3B4455;\n",
              "      --fill-color: #D2E3FC;\n",
              "      --hover-bg-color: #434B5C;\n",
              "      --hover-fill-color: #FFFFFF;\n",
              "      --disabled-bg-color: #3B4455;\n",
              "      --disabled-fill-color: #666;\n",
              "  }\n",
              "\n",
              "  .colab-df-quickchart {\n",
              "    background-color: var(--bg-color);\n",
              "    border: none;\n",
              "    border-radius: 50%;\n",
              "    cursor: pointer;\n",
              "    display: none;\n",
              "    fill: var(--fill-color);\n",
              "    height: 32px;\n",
              "    padding: 0;\n",
              "    width: 32px;\n",
              "  }\n",
              "\n",
              "  .colab-df-quickchart:hover {\n",
              "    background-color: var(--hover-bg-color);\n",
              "    box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);\n",
              "    fill: var(--button-hover-fill-color);\n",
              "  }\n",
              "\n",
              "  .colab-df-quickchart-complete:disabled,\n",
              "  .colab-df-quickchart-complete:disabled:hover {\n",
              "    background-color: var(--disabled-bg-color);\n",
              "    fill: var(--disabled-fill-color);\n",
              "    box-shadow: none;\n",
              "  }\n",
              "\n",
              "  .colab-df-spinner {\n",
              "    border: 2px solid var(--fill-color);\n",
              "    border-color: transparent;\n",
              "    border-bottom-color: var(--fill-color);\n",
              "    animation:\n",
              "      spin 1s steps(1) infinite;\n",
              "  }\n",
              "\n",
              "  @keyframes spin {\n",
              "    0% {\n",
              "      border-color: transparent;\n",
              "      border-bottom-color: var(--fill-color);\n",
              "      border-left-color: var(--fill-color);\n",
              "    }\n",
              "    20% {\n",
              "      border-color: transparent;\n",
              "      border-left-color: var(--fill-color);\n",
              "      border-top-color: var(--fill-color);\n",
              "    }\n",
              "    30% {\n",
              "      border-color: transparent;\n",
              "      border-left-color: var(--fill-color);\n",
              "      border-top-color: var(--fill-color);\n",
              "      border-right-color: var(--fill-color);\n",
              "    }\n",
              "    40% {\n",
              "      border-color: transparent;\n",
              "      border-right-color: var(--fill-color);\n",
              "      border-top-color: var(--fill-color);\n",
              "    }\n",
              "    60% {\n",
              "      border-color: transparent;\n",
              "      border-right-color: var(--fill-color);\n",
              "    }\n",
              "    80% {\n",
              "      border-color: transparent;\n",
              "      border-right-color: var(--fill-color);\n",
              "      border-bottom-color: var(--fill-color);\n",
              "    }\n",
              "    90% {\n",
              "      border-color: transparent;\n",
              "      border-bottom-color: var(--fill-color);\n",
              "    }\n",
              "  }\n",
              "</style>\n",
              "\n",
              "  <script>\n",
              "    async function quickchart(key) {\n",
              "      const quickchartButtonEl =\n",
              "        document.querySelector('#' + key + ' button');\n",
              "      quickchartButtonEl.disabled = true;  // To prevent multiple clicks.\n",
              "      quickchartButtonEl.classList.add('colab-df-spinner');\n",
              "      try {\n",
              "        const charts = await google.colab.kernel.invokeFunction(\n",
              "            'suggestCharts', [key], {});\n",
              "      } catch (error) {\n",
              "        console.error('Error during call to suggestCharts:', error);\n",
              "      }\n",
              "      quickchartButtonEl.classList.remove('colab-df-spinner');\n",
              "      quickchartButtonEl.classList.add('colab-df-quickchart-complete');\n",
              "    }\n",
              "    (() => {\n",
              "      let quickchartButtonEl =\n",
              "        document.querySelector('#df-01493f9e-575e-4a02-ae0d-290db55c7cc2 button');\n",
              "      quickchartButtonEl.style.display =\n",
              "        google.colab.kernel.accessAllowed ? 'block' : 'none';\n",
              "    })();\n",
              "  </script>\n",
              "</div>\n",
              "\n",
              "  <div id=\"id_c6ae3475-5fbd-4565-8fb9-3f82c991281a\">\n",
              "    <style>\n",
              "      .colab-df-generate {\n",
              "        background-color: #E8F0FE;\n",
              "        border: none;\n",
              "        border-radius: 50%;\n",
              "        cursor: pointer;\n",
              "        display: none;\n",
              "        fill: #1967D2;\n",
              "        height: 32px;\n",
              "        padding: 0 0 0 0;\n",
              "        width: 32px;\n",
              "      }\n",
              "\n",
              "      .colab-df-generate:hover {\n",
              "        background-color: #E2EBFA;\n",
              "        box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);\n",
              "        fill: #174EA6;\n",
              "      }\n",
              "\n",
              "      [theme=dark] .colab-df-generate {\n",
              "        background-color: #3B4455;\n",
              "        fill: #D2E3FC;\n",
              "      }\n",
              "\n",
              "      [theme=dark] .colab-df-generate:hover {\n",
              "        background-color: #434B5C;\n",
              "        box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);\n",
              "        filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));\n",
              "        fill: #FFFFFF;\n",
              "      }\n",
              "    </style>\n",
              "    <button class=\"colab-df-generate\" onclick=\"generateWithVariable('all_loads_df')\"\n",
              "            title=\"Generate code using this dataframe.\"\n",
              "            style=\"display:none;\">\n",
              "\n",
              "  <svg xmlns=\"http://www.w3.org/2000/svg\" height=\"24px\"viewBox=\"0 0 24 24\"\n",
              "       width=\"24px\">\n",
              "    <path d=\"M7,19H8.4L18.45,9,17,7.55,7,17.6ZM5,21V16.75L18.45,3.32a2,2,0,0,1,2.83,0l1.4,1.43a1.91,1.91,0,0,1,.58,1.4,1.91,1.91,0,0,1-.58,1.4L9.25,21ZM18.45,9,17,7.55Zm-12,3A5.31,5.31,0,0,0,4.9,8.1,5.31,5.31,0,0,0,1,6.5,5.31,5.31,0,0,0,4.9,4.9,5.31,5.31,0,0,0,6.5,1,5.31,5.31,0,0,0,8.1,4.9,5.31,5.31,0,0,0,12,6.5,5.46,5.46,0,0,0,6.5,12Z\"/>\n",
              "  </svg>\n",
              "    </button>\n",
              "    <script>\n",
              "      (() => {\n",
              "      const buttonEl =\n",
              "        document.querySelector('#id_c6ae3475-5fbd-4565-8fb9-3f82c991281a button.colab-df-generate');\n",
              "      buttonEl.style.display =\n",
              "        google.colab.kernel.accessAllowed ? 'block' : 'none';\n",
              "\n",
              "      buttonEl.onclick = () => {\n",
              "        google.colab.notebook.generateWithVariable('all_loads_df');\n",
              "      }\n",
              "      })();\n",
              "    </script>\n",
              "  </div>\n",
              "\n",
              "    </div>\n",
              "  </div>\n"
            ],
            "application/vnd.google.colaboratory.intrinsic+json": {
              "type": "dataframe",
              "variable_name": "all_loads_df",
              "summary": "{\n  \"name\": \"all_loads_df\",\n  \"rows\": 100,\n  \"fields\": [\n    {\n      \"column\": \"Deadhead Mileage\",\n      \"properties\": {\n        \"dtype\": \"number\",\n        \"std\": 32.169981914257214,\n        \"min\": 89.8,\n        \"max\": 259.0,\n        \"num_unique_values\": 18,\n        \"samples\": [\n          177.0,\n          191.0,\n          259.0\n        ],\n        \"semantic_type\": \"\",\n        \"description\": \"\"\n      }\n    },\n    {\n      \"column\": \"Load #\",\n      \"properties\": {\n        \"dtype\": \"number\",\n        \"std\": 16415,\n        \"min\": 137696026,\n        \"max\": 137751600,\n        \"num_unique_values\": 100,\n        \"samples\": [\n          137735853,\n          137716328,\n          137711829\n        ],\n        \"semantic_type\": \"\",\n        \"description\": \"\"\n      }\n    },\n    {\n      \"column\": \"Trailer Type\",\n      \"properties\": {\n        \"dtype\": \"category\",\n        \"num_unique_values\": 14,\n        \"samples\": [\n          \"48FL\",\n          \"FLHS\",\n          \"53VN, VAN\"\n        ],\n        \"semantic_type\": \"\",\n        \"description\": \"\"\n      }\n    },\n    {\n      \"column\": \"Origin\",\n      \"properties\": {\n        \"dtype\": \"category\",\n        \"num_unique_values\": 21,\n        \"samples\": [\n          \"NORTH CHARLESTON, SOUTH CAROLINA\",\n          \"LINCOLNTON, NORTH CAROLINA\",\n          \"CHARLOTTE, NORTH CAROLINA\"\n        ],\n        \"semantic_type\": \"\",\n        \"description\": \"\"\n      }\n    },\n    {\n      \"column\": \"Destination\",\n      \"properties\": {\n        \"dtype\": \"category\",\n        \"num_unique_values\": 28,\n        \"samples\": [\n          \"DURHAM, NORTH CAROLINA\",\n          \"COLUMBUS, GEORGIA\",\n          \"LELAND, NORTH CAROLINA\"\n        ],\n        \"semantic_type\": \"\",\n        \"description\": \"\"\n      }\n    },\n    {\n      \"column\": \"Carrier Pay\",\n      \"properties\": {\n        \"dtype\": \"number\",\n        \"std\": 308.4369774294551,\n        \"min\": 312.0,\n        \"max\": 2700.0,\n        \"num_unique_values\": 24,\n        \"samples\": [\n          800.0,\n          566.55,\n          2700.0\n        ],\n        \"semantic_type\": \"\",\n        \"description\": \"\"\n      }\n    }\n  ]\n}"
            }
          },
          "metadata": {},
          "execution_count": 63
        }
      ]
    }
  ]
}