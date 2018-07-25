# ------------------------------
# SANKEY WITH GOOGLE VIS
#    PSEUDO RESPONSIVE
# ------------------------------
#install.packages("RInno")
#install.packages("googleVis")
#install.packages("RODBC")
#install.packages("shiny")

# librairies
library(googleVis)
library(shiny)
library(RODBC)


# variables
ratio = 0.3

# App
server <- function(input, output) {
  
  getContainerDimension = reactive({
    
    dimensions = list(
      width  = paste0(input$containerGvis, "px"),
      height = paste0(input$containerGvis*ratio, "px")
    )
    
    if(is.null(input$containerGvis)){
      dimensions$width = "automatic"
      dimensions$height = "200px"
    }
    
    return(dimensions)
  })
  
  getConntoDb = reactive({
    #jdbc connection to SQLSERVER
    dbhandle <- odbcDriverConnect(connection="Driver={SQL Server};server=#####;database=#####;trusted_connection=yes;")
    
    # return data from view dbo.GreenFlow
    datSK <- sqlQuery(dbhandle, 'SELECT ParentName, ChildName,value FROM [table] ORDER BY 1')
    close(dbhandle)
  
    return (datSK)
  })
  
  getSankey = eventReactive(input$containerGvis, {
    gvisSankey(
      getConntoDb(),
      from    = "ParentName",
      to      = "ChildName",
      weight  = "value",
      options = list(
        width  = getContainerDimension()$width,
        height = getContainerDimension()$height,
        sankey="{
        node: {
        label: { 
        fontName: 'Arial',
        fontSize: 12,
        bold: false
        } 
        },
        link: {
        colors: { fill: '#a61d4c', fillOpacity: 0.8 }
        }
  }"
         ))
    }, ignoreNULL = TRUE)
  
  output$gvis = renderGvis(
    getSankey()
  )
  }

ui <- fluidPage(
  titlePanel ("Flow Hierarchy"),
  fluidRow(
    column(
      width = 12,
      tags$div(
        id = "container-gvis",
        htmlOutput("gvis", container = tags$div)
      )
    ),
    tags$script(type = "text/javascript", '
                $(document).on("shiny:connected", function(event) {
                Shiny.onInputChange("containerGvis", $("#container-gvis").innerWidth());
                });
                $(window).resize(function() {
                waitForFinalEvent(function(){
                var width = $("#container-gvis").innerWidth();
                console.log(width);
                Shiny.onInputChange("containerGvis", width);
                }, 250, "idContainerGvis");
                });
                var waitForFinalEvent = (function () {
                var timers = {};
                return function (callback, ms, uniqueId) {
                if (timers[uniqueId]) {
                clearTimeout (timers[uniqueId]);
                }
                timers[uniqueId] = setTimeout(callback, ms);
                };
                })();
                ')
    )
  )


#shinyApp(ui = ui, server = server)
runApp(list(ui = ui, server = server),host="XX.XX.XX.XX",port=XXXX, launch.browser = TRUE)