"""
Usage:
  qualifications_score_charts.py --input=<dir> --output=<dir>

"""


import docopt
import os
import pandas as pd
import sys

args = docopt.docopt(__doc__, version='printbook v 1.0')


input_path=args['--input']
if( not os.path.exists(input_path)):
    print(f"File {input_path} not found")
    sys.exit(-1)

output_path=args['--output']
if( not os.path.exists(output_path)):
    print(f"Directory {output_path} not found")
    sys.exit(-1)


text0 = ""
text1 = ""
text2 = ""

is_first = True
print("Creating HTML view")
for file in os.listdir(input_path):
    print(f"File analized: {file}")
    df = pd.read_csv(os.path.join(input_path, file))
    data_list = []
    for n in range(101):
        i = n/10
        data_in_frame = df[(df.qualification_score>round(i-0.1, 1))&(df.qualification_score<=i)]
        language_score = round(data_in_frame.language_score.mean(), 1)
        url_score = round(data_in_frame.url_score.mean()/10, 1)
        punctuation_score = round(data_in_frame.punctuation_score.mean()/10, 1)
        bad_chars_score = round(data_in_frame.bad_chars_score.mean()/10, 1)
        numbers_score = round(data_in_frame.numbers_score.mean()/10, 1)
        repeated_score = round(data_in_frame.repeated_score.mean()/10, 1)
        n_big_segments_score = round(data_in_frame.n_big_segments_score.mean()/10, 1)
        great_segment_score = round(data_in_frame.great_segment_score.mean()/10, 1)
        data_list.append([i, data_in_frame.shape[0], f"cstm({i}, {language_score}, {url_score}, {punctuation_score}, {bad_chars_score}, {numbers_score}, {repeated_score}, {n_big_segments_score}, {great_segment_score})"])
    
    
    if is_first:
        text0 = f"[['Score', 'Count'," +"{'type': 'string', 'role': 'tooltip', 'p': {'html': true}}]" + f", {', '.join([str(x) for x in data_list])}];"
        text1 += f"if (selectedValue === '{file.split('_')[0]}') {'{'}\n            newData = [['Score', 'Count'," +"{'type': 'string', 'role': 'tooltip', 'p': {'html': true}}]" + f", {', '.join([str(x) for x in data_list])}];\n"
        is_first = False

    else:
        
        text1 += f"          {'}'} else if (selectedValue === '{file.split('_')[0]}') {'{'}\n            newData = [['Score', 'Count'," +"{'type': 'string', 'role': 'tooltip', 'p': {'html': true}}]" + f", {', '.join([str(x) for x in data_list])}];\n"
    text2 += f'<option value="{file.split("_")[0]}">{file.split("_")[0]}</option>\n'

text0 = text0.replace("'cstm", "cstm").replace("']", "]").replace("nan", "null")
text1 = text1.replace("'cstm", "cstm").replace("']", "]").replace("nan", "null")


html = """

<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load("current", {packages:["corechart"]});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {
        // Definir los datos iniciales
        var initialData = __DATA0__

        function colorLanguageScore(value, minScore = 0, maxScore = 1,  color1 = '#FF0000', color2 = '#b5ff42') {
          
          if (value < minScore) {
            value = minScore;
          }

          if (value > maxScore) {
            value = maxScore;
          }
          
          // Convertimos los colores de hexadecimal a RGB
            let normalizedValue = (value - minScore) / (maxScore - minScore);

            // Convertimos los colores de hexadecimal a RGB
            let r1 = parseInt(color1.substring(1, 3), 16);
            let g1 = parseInt(color1.substring(3, 5), 16);
            let b1 = parseInt(color1.substring(5, 7), 16);

            let r2 = parseInt(color2.substring(1, 3), 16);
            let g2 = parseInt(color2.substring(3, 5), 16);
            let b2 = parseInt(color2.substring(5, 7), 16);

            // Calculamos la diferencia entre los componentes de color
            let dr = r2 - r1;
            let dg = g2 - g1;
            let db = b2 - b1;

            // Interpolamos los componentes de color
            let r = Math.round(r1 + dr * normalizedValue);
            let g = Math.round(g1 + dg * normalizedValue);
            let b = Math.round(b1 + db * normalizedValue);

            // Convertimos los componentes de color de nuevo a hexadecimal
            let hexR = r.toString(16).padStart(2, '0');
            let hexG = g.toString(16).padStart(2, '0');
            let hexB = b.toString(16).padStart(2, '0');

            // Combinamos los componentes de color en un solo string hexadecimal
            return '#' + hexR + hexG + hexB;
        }
        
        function cstm(qualificationScore, languageScore, urlgeScore, punctScore, badCharsScore, numbersScore, spamScore, nBigSegmentsScore, greatSegmentScore) {
          return '<div style="padding:5px;">' +
              '<table>' + '<tr>' +
              '<th style="border-bottom: solid 1px; padding-bottom: 5px; text-transform: uppercase;">Scores</th>' + '</tr>' + '<tr>' +
              '<td><b>Qualification score: </b><span>' + qualificationScore + '</span></td>' + '</tr>' + '<tr>' +
              '<td><b>Language score: </b><span class="score">' + languageScore + '<span class="color" style="background-color: ' + colorLanguageScore(languageScore) +'; "></span></span></td>' + '</tr>' + '<tr>' +
              '<td><b>URL score: </b><span class="score">' + urlgeScore + '<span class="color" style="background-color: ' + colorLanguageScore(urlgeScore, 0.5, 1) +'; "></span></span></td>' + '</tr>' + '<tr>' +
              '<td><b>Punctuation score: </b><span class="score">' + punctScore + '<span class="color" style="background-color: ' + colorLanguageScore(punctScore, 0.5, 1) +'; "></span></span></td>' + '</tr>' + '<tr>' +
              '<td><b>Bad chars score: </b><span class="score">' + badCharsScore + '<span class="color" style="background-color: ' + colorLanguageScore(badCharsScore, 0.5, 1) +'; "></span></span></td>' + '</tr>' + '<tr>' +
              '<td><b>Numbers score: </b><span class="score">' + numbersScore + '<span class="color" style="background-color: ' + colorLanguageScore(numbersScore, 0.5, 1) +'; "></span></span></td>' + '</tr>' + '<tr>' +
              '<td><b>Spam score: </b><span class="score">' + spamScore + '<span class="color" style="background-color: ' + colorLanguageScore(spamScore, 0.5, 1) +'; "></span></span></td>' + '</tr>' + '<tr>' +
              '<td><b>Big segments score: </b><span class="score">' + nBigSegmentsScore + '<span class="color" style="background-color: ' + colorLanguageScore(nBigSegmentsScore, 0, 1, '#CCB22E') +'; "></span></span></td>' + '</tr>' + '<tr>' +
              '<td><b>Great segments score: </b><span class="score">' + greatSegmentScore + '<span class="color" style="background-color: ' + colorLanguageScore(greatSegmentScore, 0, 1, '#CCB22E') +'; "></span></span></td>' + '</tr>' + '</table>' + '</div>';
        }      
        
        
        drawColumnChart(initialData); // Dibujar el gráfico inicial

        // Manejar el cambio en el select
        document.getElementById('dataSelect').addEventListener('change', function() {
          var selectedValue = this.value;
          var newData;

          // Seleccionar los datos apropiados según la opción elegida
          
          __DATA1__

          drawColumnChart(newData); // Dibujar el gráfico con los nuevos datos
        });
      }

      function drawColumnChart(data) {
        var options = {
          title: 'Score of qualification',
          legend: { position: 'none' },
          colors: ['#FFA633'],
          tooltip: { isHtml: true } // Habilitar tooltip con HTML
          
        };

        var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
        chart.draw(google.visualization.arrayToDataTable(data), options);
      
      }
    </script>
  </head>
  <style>
    html {
      font-family: arial;
    }

    .container {
      width: 100%;
      max-width: 1000px;
      margin: auto;
      display: flex;
      flex-wrap: wrap;
      height: 70vh;
      align-items: center;
      justify-content: center;
    }

    .container p {
      width: 100%;
      font-size: 1.2rem;
      text-align: center;
      margin-top: 50px;
      font-weight: bold;
    }

    .container select {
      padding: 2px 5px;
      font-size: 1rem;
      border-radius: 25px;
      margin-left: 10px;
    }

    #chart_div {
      width: 100%; 
      height: 700px;
    }

    .score {
      display: inline-flex; 
      justify-content: center; 
      align-items:flex-start;
    }

    .color {
      height:15px; 
      width: 15px; 
      border-radius: 50%; 
      margin-left: 5px
    }

    td {
      padding-top: 10px
    }
  </style>
  <body>
    <div class="container">
      <!-- Agregar el select para elegir los datos -->
    <p>Select language <select id="dataSelect">
      
        __DATA2__

    </select></p>
    
    <!-- Div para el gráfico -->
    <div id="chart_div"></div>
    </div>
    
  </body>
</html>


"""


html = html.replace("__DATA0__", text0)
html = html.replace("__DATA1__", text1+"\n}")
html = html.replace("__DATA2__", text2)

with open(os.path.join(output_path, "qualifier_scores.html"), "w", encoding="utf8") as file:
    file.write(html)

    