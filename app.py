from flask import Flask, render_template, request, send_file
import pandas
import folium
from geopy.geocoders import Nominatim
import datetime

app = Flask(__name__)


@app.route('/')
def home():

    return render_template("home.html")


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/success/', methods=['POST'])
def success():
    # creating a global variable to use between functions (generate_map())
    global filename
    global lat
    global lon
    global marker_name

    if request.method == 'POST':
        email = request.form["email_name"]
        try:
            file = request.files["file_csv"]
        except:
            return render_template("home.html")

        try:
            # creating DataFrame that reads a file
            df = pandas.read_csv(file)
            gc = Nominatim()
            # creating a temporary pandas Data Frame column (Series) object to geocode coordinates from
            df["Coordinates"] = df["Address"].apply(gc.geocode)
            df["Latitude"] = df["Coordinates"].apply(lambda x: x.latitude if x is not None else None)
            df["Longitude"] = df["Coordinates"].apply(lambda x: x.longitude if x is not None else None)

            # updating global variables to use in map creating functions
            lat = list(df["Latitude"])
            lon = list(df["Longitude"])
            marker_name = list(df["Address"])

            # deleting temporary pandas column, parameter "1" means we drop column
            df = df.drop("Coordinates", 1)
            # generating csv file that will be downloaded by user
            filename = datetime.datetime.now().strftime("uploads/%Y-%m-%d-%H-%M-%S-%f"+".csv")
            df.to_csv(filename, index=None)
            return render_template("success.html", email=email, df_html=df.to_html(), btn_download="download.html")
        except:
            return render_template("home.html", df_html="Please make sure your CSV file has an address column.")


@app.route('/manual/')
def manual():
    f = open("uploads/records.csv", "w+")
    f.write("Address,\n")
    f.close
    return render_template("manual.html")


@app.route('/record/', methods=['POST'])
def record():
    if request.method == 'POST':
        f = open("uploads/records.csv", "a+")
        f.write((request.form["address_name"]).replace(",", "") + ",\n")
        f.close()
        return render_template("manual.html")


@app.route('/manual_success/', methods=['POST'])
def manual_success():
    # creating a global variable to use between functions (generate_map())
    global filename
    global lat
    global lon
    global marker_name

    if request.method == 'POST':

        file = "uploads/records.csv"
        df = pandas.read_csv(file)
        gc = Nominatim()
        # creating a temporary pandas Data Frame column (Series) object to geocode coordinates from
        df["Coordinates"] = df["Address"].apply(gc.geocode)
        df["Latitude"] = df["Coordinates"].apply(lambda x: x.latitude if x is not None else None)
        df["Longitude"] = df["Coordinates"].apply(lambda x: x.longitude if x is not None else None)

        # updating global variables to use in map creating functions
        lat = list(df["Latitude"])
        lon = list(df["Longitude"])
        marker_name = list(df["Address"])

        # deleting temporary pandas column, parameter "1" means we drop column
        # df = df.drop("Coordinates", 1)

        # generating csv file that will be downloaded by user
        filename = datetime.datetime.now().strftime("uploads/%Y-%m-%d-%H-%M-%S-%f" + ".csv")
        df.to_csv(filename, index=None)
        return render_template("manual_success.html", address="address", df_html=df.to_html(), btn_download="download.html")



@app.route('/download-file/')
def download():
    return send_file(filename, attachment_filename="yourfile.csv", as_attachment=True)


@app.route('/map/')
def generate_map():
    try:
        map = folium.Map(location=[lat[0], lon[0]], zoom_start=11, tiles="OpenStreetMap")

        # Creating html variable to use html styles in popup window
        html = """
        <a href="https://www.google.com/search?q=%%22%s%%22" target="_blank">%s</a><br>
        Lat: %s<br>
        Lon: %s<br>
        """

        fg = folium.FeatureGroup(name="My Map")


        for lt, ln, mark in zip(lat, lon, marker_name):
            iframe = folium.IFrame(html=html % (mark, mark, lt, ln), width=200, height=100)
            fg.add_child(folium.Marker(location=[lt, ln], popup=folium.Popup(iframe), icon=folium.Icon(color="green")))

        map.add_child(fg)

        map.save("templates/map.html")
        return render_template("map.html")
    except:
        return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=False)



