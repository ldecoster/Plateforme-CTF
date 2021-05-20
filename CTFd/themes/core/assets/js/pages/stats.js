import "./main";
import $ from "jquery";
import CTFd from "../CTFd";
import { createGraph, updateGraph } from "../graphs";

const createGraphs = (id, name, account_id) => {
  Promise.all([
    CTFd.api.get_user_solves({ userId: account_id }),
    CTFd.api.get_user_fails({ userId: account_id }),
    CTFd.api.get_user_awards({ userId: account_id })
  ]).then(responses => {
    createGraph(
      "solve_percentages",
      "#keys-pie-graph",
      responses,
      id,
      name,
      account_id
    );
  });
};

const updateGraphs = (id, name, account_id) => {
  Promise.all([
    CTFd.api.get_user_solves({ userId: account_id }),
    CTFd.api.get_user_fails({ userId: account_id }),
    CTFd.api.get_user_awards({ userId: account_id })
  ]).then(responses => {
    updateGraph(
      "solve_percentages",
      "#keys-pie-graph",
      responses,
      id,
      name,
      account_id
    );
  });
};

$(() => {
  let id, name, account_id;
  ({ id, name, account_id } = window.stats_data);

  createGraphs(id, name, account_id);
  setInterval(() => {
    updateGraphs(id, name, account_id);
  }, 300000);
});
