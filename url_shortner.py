import mysql.connector;
import datetime;
from flask import Flask,render_template,request,redirect,url_for,flash;

config ={
    'user':'root',
    'password':'rehaan',
    'host': '127.0.0.1',
    'database': 'url_shortner'
}

app = Flask(__name__);
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
#the / indicates the url after 127.0.0.1:5000/...
@app.route('/', methods=('GET','POST'))
def index():

    #starting connection
    db = mysql.connector.connect(**config);

    #collecting db information
    dbinfo = db.get_server_info();
    print('MySQL version ', dbinfo);

    #initializing the cursor to move around the db
    cursor = db.cursor();

    #Setting cursor to the database
    cursor.execute('select database()');
    print('connected to ', cursor.fetchone());

     #function to insert data into the database
    def insertData(url,shortlink):  
        insert_query = "insert into urls (`url`, `created_on`, `shortlink`) VALUES(%s, %s, %s);"
        current_time = datetime.datetime.now();
        values = (url, current_time, shortlink);
        cursor.execute(insert_query, values);
        db.commit();
        print("Data was input");

    if request.method == 'POST':
        url=request.form.get('url');
        shortlink=request.form.get('shortlink');
        #checking if it already exists
        check_duplicates_query = 'SELECT * FROM urls WHERE shortlink = %s';
        cursor.execute(check_duplicates_query, (shortlink,));
        
        if url.startswith('http://'):
            url = 'https://'+url;
        elif not url.startswith('https://'):
            url = 'https://'+url;

        if cursor.fetchone():
            print('printing', );
            return 'Shortlink already exists for the URL';
        else:
            insertData(url,shortlink);
        
        cursor.close();
        db.close();
        shortlink = shortlink.replace(" ","-");
        short_url = request.host_url+shortlink;
        return 'Your shortlink is created: '+ short_url;
    return render_template('index.html');

@app.route("/<shortlink>")
def url_redirect(shortlink):
    db = mysql.connector.connect(**config);
    cursor = db.cursor();
    redirect_query = "SELECT url FROM urls WHERE shortlink=%s";
    original_url = cursor.execute(redirect_query, (shortlink,));
    record = cursor.fetchone();
    if not record:
        flash('INVALID URL','error');
        return redirect(url_for('index'));
    else:
        return redirect(record[0]);