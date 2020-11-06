import $ from "jquery";
import CTFd from "core/CTFd";


export function deleteTag(_event) {
  const $elem = $(this);
  const tag_id = $elem.attr("tag-id");
  const challenge_id = window.CHALLENGE_ID;
  CTFd.api.delete_tagChallenge({ tagId: tag_id, challengeId: challenge_id })
  .then(response => {
    if (response.success) {
      $elem.parent().remove();
    }
  });
}
//Todo Kylian : tag_challenges
export function setTagList(event) {

  CTFd.api.get_tag_list().then(response => {

    const tagsList = response.data;
    const $elem = $(this);
    const searchtag = $elem.val();
    
    //get match to the current input
    let matches = tagsList.filter(tag =>{
      const regex = new RegExp(`^${searchtag}`,'gi');
      console.log(tag.value);
      console.log(tag.challenges.includes(window.CHALLENGE_ID));
      return tag.value.match(regex) && ! tag.challenges.includes(window.CHALLENGE_ID);
    });

    if(searchtag.length === 0){
      matches = [];
      $(".list-group").html('');
    }

    outputHtml(matches);

    let newMatches = tagsList.filter(tag =>{
      const regex = new RegExp(`^${searchtag}`,'gi');
      return tag.value.match(regex);
    });
    if (event.keyCode != 13 || newMatches.length!=0) {
      return;
    }
    
    const params = {
      value: searchtag,
    };  
    addNewTag(params);  
  });
}
function addNewTag(params){

  CTFd.api.post_tag_list({},params).then(res => {
    console.log(res);
    CTFd.api.post_tagChallenge_list({},{ tag_id: res.data.id,challenge_id:window.CHALLENGE_ID }).then(response=>{
      if (response.success) {
        const tpl =
          "<span class='badge badge-primary mx-1 challenge-tag'>" +
          "<span>{0}</span>" +
          "<a class='btn-fa delete-tag' tag-id='{1}'>&times;</a></span>";
        const tag = $(tpl.format(params.value,res.data.id));
        $("#challenge-tags").append(tag);
        // TODO: tag deletion not working on freshly created tags
        tag.click(deleteTag);
      }
    });
  });
}

function addTag(params){

  CTFd.api.post_tagChallenge_list({},params).then(res => {
    CTFd.api.get_tag({ tagId: res.data.tag_id, }).then(response=>{
      if (response.success) {
        const tpl =
          "<span class='badge badge-primary mx-1 challenge-tag'>" +
          "<span>{0}</span>" +
          "<a class='btn-fa delete-tag' tag-id='{1}'>&times;</a></span>";
        const tag = $(tpl.format(response.data.value, response.data.id));
        $("#challenge-tags").append(tag);
        // TODO: tag deletion not working on freshly created tags
        tag.click(deleteTag);
      }
    });
  });
}

export function addClickedTag(_event){
  $elem = $(this);
    const params = {
      tag_id:$elem.attr("tag_id"),
      challenge_id:window.CHALLENGE_ID
    }
  addTag(params);
}

//show result in HTML format
const outputHtml = matches =>{
  if (matches.length > 0){
    const html = matches
    .map(
      match =>`
      <a class="list-group-item list-group-item-action list-group-item-dark" tag_id="${match.id}">${match.value}</a>
    `
    ).join('');
    $(".list-group").html(html);
  }
}