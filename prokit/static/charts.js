function proplot2(divName, scores, dates) { 
  var data = [
    {
      x: dates,
      y: scores,
      type: 'scatter',
    }
  ]; 
  var layout = {
    font: {
      size: 10,
      color: '#0',
      },	
      yaxis: {
      tickvals: [10, 20, 30, 40, 50, 60, 70, 80, 90],
      automargin: false,
      tickcolor: '#000',
    },
    xaxis: { 
      titlefont: { 
        size: 10,
      },
    },
    height: 300,
    margin: { l: 20, r: 0, b: 100, t: 0, pad: 0 },
    paper_bgcolor : 'rgba(0,0,0,0)'
  };
  Plotly.newPlot(divName, data, layout);
}


