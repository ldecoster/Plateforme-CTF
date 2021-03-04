import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "core/ezq";

function deleteSelectedBadges(_event) {
  let badgeIDs = $("input[data-badge-id]:checked").map(function() {
    return $(this).data("badge-id");
  });
  let target = badgeIDs.length === 1 ? "badge" : "badges";

  ezQuery({
    title: "Delete Badges",
    body: `Are you sure you want to delete ${badgeIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (var badID of badgeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/badges/${badID}`, {
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


function addBadge(_event){

  let badge_name = document.getElementsByName("badge_name");
  let badge_desc = document.getElementsByName("badge_desc");
  //let badge_tag = document.getElementsByName("badge_tag");
  let badge_type  = "Standard";
  const params = {
    description: "a description",
    name:"badge name",
    type: "standard",
  };
  console.log(params);
  CTFd.api.post_badge_list(params).then(res => {
    console.log(res);
  });
}




function bulkEditBadges(_event) {
  let badgeIDs = $("input[data-badge-id]:checked").map(function() {
    return $(this).data("badge-id");
  });

  ezAlert({
    title: "Edit Badges",
    body: $(`
    <form id="badges-bulk-edit">
      <div class="form-group">
        <label>State</label>
        <select name="state" data-initial="">
          <option value="">--</option>
          <option value="hidden">Hidden</option>
          <option value="visible">Visible</option>
          <option value="voting">Voting</option>
        </select>
      </div>
    </form>
    `),
    button: "Submit",
    success: function() {
      let data = $("#badges-bulk-edit").serializeJSON(true);
      const reqs = [];
      for (var badID of badgeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/badges/${badID}`, {
            method: "PATCH",
            body: JSON.stringify(data)
          })
        );
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
      });
    }
  });
}




$("#edit-new-badge").on('click',function(event){
  console.log('click detected');
  $("#badge-create-options").modal();
});

$("#badge-create-button").click(addBadge);

$(() => {
  $("#badges-delete-button").click(deleteSelectedBadges);
  $("#badges-edit-button").click(bulkEditBadges);
});
