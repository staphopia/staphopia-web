function generate_sequencing_center_chart() {
    Highcharts.chart('sequencing-centers', {
        data: { table: 'sequencing-centers-table'},
        chart: { type: 'column' },
        legend: { enabled: false },
        title: { text: 'Top 10 S. aureus Sequencing Contributors'},
        xAxis: {
            type: 'category',
            labels: {
                rotation: -45,
                useHTML: true,
                style: {
                    fontSize: '12px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        yAxis: {
            type: 'logarithmic',
            allowDecimals: false,
            title: { text: 'Total Samples In ENA Database' }
        },
        plotOptions: {
            column: {
                dataLabels: {
                    enabled: true
                }
            }
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.series.name + '</b><br/>' +
                    this.point.y + ' ' + this.point.name;
            }
        }
    });
}

function generate_mlst_chart() {
    Highcharts.chart('mlst', {
        data: { table: 'mlst-table'},
        chart: { type: 'column'},
        legend: { enabled: false },
        title: { text: 'Top 10 S. aureus Sequenced MLSTs'},
        xAxis: {
            type: 'category',
            labels: {
                rotation: -45,
                useHTML: true,
                style: {
                    fontSize: '12px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        yAxis: {
            type: 'logarithmic',
            allowDecimals: false,
            title: { text: 'Total Samples' }
        },
        plotOptions: {
            column: {
                dataLabels: {
                    enabled: true
                }
            }
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.series.name + '</b><br/>' +
                    this.point.y + ' ' + this.point.name;
            }
        }
    });
}
