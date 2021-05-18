import $ from "jquery";
import echarts from "echarts/dist/echarts-en.common";

const graph_configs = {
  solve_percentages: {
    format: (id, name, account_id, responses) => {
      const solves_count = responses[0].data.length;
      const fails_count = responses[1].meta.count;
      let option = {
        title: {
          left: "center",
          text: "Solve Percentages"
        },
        tooltip: {
          trigger: "item"
        },
        toolbox: {
          show: true,
          feature: {
            saveAsImage: {}
          }
        },
        legend: {
          orient: "vertical",
          top: "middle",
          right: 0,
          data: ["Fails", "Solves"]
        },
        series: [
          {
            name: "Solve Percentages",
            type: "pie",
            radius: ["30%", "50%"],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: "center"
            },
            itemStyle: {
              normal: {
                label: {
                  show: true,
                  formatter: function(data) {
                    return `${data.name} - ${data.value} (${data.percent}%)`;
                  }
                },
                labelLine: {
                  show: true
                }
              },
              emphasis: {
                label: {
                  show: true,
                  position: "center",
                  textStyle: {
                    fontSize: "14",
                    fontWeight: "normal"
                  }
                }
              }
            },
            emphasis: {
              label: {
                show: true,
                fontSize: "30",
                fontWeight: "bold"
              }
            },
            labelLine: {
              show: false
            },
            data: [
              {
                value: fails_count,
                name: "Fails",
                itemStyle: { color: "rgb(207, 38, 0)" }
              },
              {
                value: solves_count,
                name: "Solves",
                itemStyle: { color: "rgb(0, 209, 64)" }
              }
            ]
          }
        ]
      };

      return option;
    }
  }
};

export function createGraph(
  graph_type,
  target,
  data,
  id,
  name,
  account_id
) {
  const cfg = graph_configs[graph_type];
  let chart = echarts.init(document.querySelector(target));
  chart.setOption(cfg.format(id, name, account_id, data));
  $(window).on("resize", function() {
    if (chart != null && chart != undefined) {
      chart.resize();
    }
  });
}

export function updateGraph(
  graph_type,
  target,
  data,
  id,
  name,
  account_id
) {
  const cfg = graph_configs[graph_type];
  let chart = echarts.init(document.querySelector(target));
  chart.setOption(cfg.format(id, name, account_id, data));
}

export function disposeGraph(target) {
  echarts.dispose(document.querySelector(target));
}
