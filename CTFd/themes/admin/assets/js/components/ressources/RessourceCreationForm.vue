<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header text-center">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3>Ressource</h3>
              </div>
            </div>
          </div>
          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <form method="POST" @submit.prevent="submitRessource">
          <div class="modal-body">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <div class="form-group">
                    <label class="text-muted">
                      Ressource<br />
                      <small>Markdown &amp; HTML are supported</small>
                    </label>
                    <textarea
                      type="text"
                      class="form-control markdown"
                      name="content"
                      rows="7"
                      ref="content"
                    ></textarea>
                  </div>
                  <input type="hidden" id="ressource-id-for-ressource" name="id" />
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <button class="btn btn-success float-right">Submit</button>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RessourceCreationForm",
  props: {
    challenge_id: Number
  },
  data: function() {
    return {};
  },
  methods: {
    getContent: function() {
      return this.$refs.content.value;
    },
    submitRessource: function() {
      let params = {
        challenge_id: this.$props.challenge_id,
        content: this.getContent()
      };
      CTFd.fetch("/api/v1/ressources", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.$emit("refreshRessources", this.$options.name);
          }
        });
    }
  }
};
</script>

<style scoped></style>