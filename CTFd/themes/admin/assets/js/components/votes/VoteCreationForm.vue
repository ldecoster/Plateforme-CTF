<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header text-center">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3>Voting</h3>
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
        <form method="POST" @submit.prevent="submitVote">
          <div class="modal-body">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <div class="form-group">
                    <label class="text-muted">
                      Select your vote
                    </label>
                    <div class="form-group">
                      <select class="form-control custom-select" name="value" ref="value">
                        <option value="1">Positive</option>
                        <option value="0">Negative</option>
                      </select>
                    </div>
                  </div>
                  <input type="hidden" id="vote-id-for-vote" name="id" />
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <button class="btn btn-primary float-right">Submit</button>
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
  name: "VoteCreationForm",
  props: {
    challenge_id: Number
  },
  data: function() {
    return {};
  },
  methods: {
    getValue: function() {
      return this.$refs.value.value;
    },
    submitVote: function() {
      let params = {
        challenge_id: this.$props.challenge_id,
        value: this.getValue()
      };
      CTFd.fetch("/api/v1/votes", {
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
            this.$emit("refreshVotes", this.$options.name);
          }
        });
    }
  }
};
</script>

<style scoped></style>