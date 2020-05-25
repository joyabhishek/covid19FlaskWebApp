from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from bokeh.models.formatters import DatetimeTickFormatter,NumeralTickFormatter
from bokeh.models import HoverTool
from bokeh.models import Circle

def plotGraph(df, color):
	source = ColumnDataSource(df)
	hover = HoverTool(
	    tooltips=[
	        ("Total Cases","@totalconfirmed{0,0}"),
	        ("Date",'@date{%d-%b}')
	    ], 
	    formatters={
	        "@date": "datetime"
	    }
	)
	p=figure(x_axis_type='datetime',y_range=(int(df.iloc[0]['totalconfirmed'])-100, int(df.iloc[-1]['totalconfirmed'])+10000),tools=[hover],plot_width=800, plot_height=400,x_axis_label='Date',y_axis_label='No. of cases',sizing_mode='scale_width')
	p.line(x='date',y='totalconfirmed',source=source,color=color,line_width=3,line_alpha=0.2)
	renderer = p.circle(x='date',y='totalconfirmed',source=source,color=color,size=5,legend_label="Total confirmed cases")

	p.axis.axis_label_text_font_style = 'normal'
	p.axis.axis_label_text_color = color

	#x_axis attributes
	p.xaxis.formatter = DatetimeTickFormatter(months=['%d-%b'])
	p.xaxis.axis_line_color = color
	p.xaxis.major_label_text_color = color
	p.xaxis.axis_line_width = 1
	p.xgrid.grid_line_color = None

	#y_axis attributes
	p.yaxis.formatter = NumeralTickFormatter(format="0 a")
	p.yaxis.axis_line_color = color
	p.yaxis.major_label_text_color = color
	p.yaxis.axis_line_width = 1
	p.ygrid.grid_line_color = color
	p.ygrid.grid_line_alpha = 0.1

	#ticks styling
	p.axis.minor_tick_line_color = None
	#p.axis.minor_tick_line_width = 2
	p.axis.major_tick_line_color = color


	#Plot background attribute
	p.background_fill_color = color
	p.background_fill_alpha = 0.1

	#Legend
	p.legend.location = "top_left"
	p.legend.label_text_color = color
	p.legend.background_fill_alpha = 0
	p.legend.border_line_color = color

	return components(p)