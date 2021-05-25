import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import {ezQuery} from "core/ezq";

function deleteSelectedBadges() {
  let badgeIDs = $("input[data-badge-id]:checked").map(function() {
    return $(this).data("badge-id");
  });
  let target = badgeIDs.length === 1 ? "badge" : "badges";

  ezQuery({
    title: "Delete Badges",
    body: `Are you sure you want to delete ${badgeIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (let badgeID of badgeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/badges/${badgeID}`, {
            method: "DELETE"
          })
        );
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
      });
    }
  });
}

$(() => {
    $("#badges-delete-button").click(deleteSelectedBadges);
});