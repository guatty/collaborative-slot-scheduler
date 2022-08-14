<template>
  <div class="home">
    <h3>Liste des membres inscrits en D1</h3>
    <h4 v-if="hasNoData">
      Vous n'avez pas le droit de consulter les données personnelles des
      membres.
    </h4>
    <template v-else>
      <!-- <label for="hideinactive">Cacher les membres non actifs (erasmus, démission, ...)</label> -->
      <input type="checkbox" id="hideinactive" v-model="hideinactive">
      <table-lite
        :is-slot-mode="true"
        :has-checkbox="false"
        :is-loading="table.isLoading"
        :is-re-search="table.isReSearch"
        :columns="table.columns"
        :rows="membersD1"
        :total="membersD1.length"
        @do-search="doSearch"
        @is-finished="tableLoadingFinish"
        @return-checked-rows="updateCheckedRows"
      >
        <template v-slot:lastname>
              fff      
        </template>
      </table-lite>

    <UserModal
      ref="modalName"
      v-show="isUserModalVisible"
      @closeModal="closeUserModal"
      v-bind="userModalModel"
      @refresh="transmitRefresh"
    />
    </template>
  </div>
</template>

<script>
import TableLite from "vue3-table-lite";
import { Http } from "@capacitor-community/http";
import UserModal from "../components/Modal";
export default {
  name: "MembresD1",
  components: { TableLite, UserModal },
  data() {
    return {
      sortable: true,
      membersD1: [],
      hasNoData: false,
      hideinactive: true,
      isUserModalVisible: false,
      userModalModel: {},
      table: {
        messages: {
          pagingInfo: "{0}-{1} sur {2}",
          pageSizeChangeLabel: "Nombre de membres :",
          gotoPageLabel: "Page :",
          noDataAvailable: "Chargement en cours...",
        },
        isLoading: false,
        isReSearch: false,
        columns: [
          {
            label: "Prénom",
            field: "firstname",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.firstname;
            },
          },
          {
            label: "Nom",
            field: "lastname",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.lastname;
            },
          },
          {
            label: "Contribution P2",
            field: "contribution_p2",
            width: "15%",
            sortable: true,
            display: function (row) {
              var [scribe, relecture] = row.contribution_p2.split(":");
              if (scribe < 2 && parseInt(scribe) + parseInt(relecture) < 4) {
                return '<p style="color:black; background-color:red; font-weight:bold; ">N\'a pas rempli ses engagements APECS</p>';
              } else if (scribe >= 3 && parseInt(scribe) + parseInt(relecture) >= 7) {
                return "<p style=\"color:black; background-color:#65FF00; font-weight:bold;\">S'est plus qu'impliqué</p>";
              } else {
                return '<p style="">A respecté ses engagements</p>';
              }
            },
          },
          {
            label: "Contribution D1",
            field: "contribution_d1",
            width: "9%",
            sortable: true,
            display: function (row) {
              if (row.cat == null) {
                return '<p style="color:red;">Ne s\'est pas encore inscrit·e sur le planning.</p>';
              } else if (
                (row.cat["h_scribe"] >= 3 && row.cat["h_proofread"] >= 3) ||
                (row.cat["h_scribe"] >= 2 &&
                  row.cat["h_proofread"] >= 2 &&
                  row.contribution_p2
                    .split(":")
                    .reduce((partial_sum, a) => partial_sum + a, 0) >= 4)
              ) {
                return '<p style="color:green;">A pris ses heures ! (S'+row.cat["h_scribe"]+'R'+row.cat["h_proofread"]+') </p>';
              } else {
                return '<p style="color:red;">N\'a pas pris suffisamment d\'heures. (S'+row.cat["h_scribe"]+'R'+row.cat["h_proofread"]+') </p>';
              }
            },
          },
          {
            label: "Mail",
            field: "mail",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.mail;
            },
          },
          {
            label: "Promo",
            field: "school_year",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.school_year;
            },
          },
          {
            label: "Droits",
            field: "right_group",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.right_group;
            },
          },
          {
            label: "Inscription",
            field: "active_kind",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.active_kind;
            },
          },
          {
            label: "🖆",
            field: "edit",
            width: "2%",
            sortable: true,
            display: function (row) {
              return '<button data-mail="'+row.mail+'" rel="noopener noreferrer" class="btn quick-btn">🖆</button>'
            },
          },
          // {
          //   label: "ID",
          //   field: "id",
          //   width: "3%",
          //   sortable: true,
          //   isKey: true,
          // },
          // {
          //   label: "Name",
          //   field: "name",
          //   width: "10%",
          //   sortable: true,
          //   display: function (row) {
          //     return (
          //       '<a href="#" data-id="' + row.user_id + '" class="name-btn">' + row.name + "</button>"
          //     );
          //   },
          // },
          // {
          //   label: "Email",
          //   field: "email",
          //   width: "15%",
          //   sortable: true,
          // },
          // {
          //   label: "",
          //   field: "quick",
          //   width: "10%",
          //   display: function (row) {
          //     return (
          //       '<button type="button" data-id="' + row.user_id + '" class="quick-btn">Button</button>'
          //     );
          //   },
          // },
        ],
        rows: [
          {
            id: 1,
            name: "TEST1",
          },
        ],
      },
    };
  },
  computed: {
    loggedIn() {
      return this.$store.getters["auth/isAuthenticated"];
    },
  },
  created() {
    if (!this.loggedIn) {
      this.$router.push({ name: "LoginD1" });
    }
  },
  mounted() {
    this.refreshMembers();
  },
  watch: {
    hideinactive: function() { this.refreshMembers(); }
  },
  methods: {
    showUserModal(row) {
      this.userModalModel = {
        mail: row.mail,
        firstname: row.firstname,
        lastname: row.lastname,
        settings: row.settings,
      };
      this.isUserModalVisible = true;
    },
    closeUserModal() {
      this.isUserModalVisible = false;
    },
    tableLoadingFinish (elements) {
      console.log(elements);
      Array.prototype.forEach.call(elements, function (element) {
        console.log("bruh1");
        if (element.classList.contains("quick-btn")) {
          element.addEventListener("click", function () {
            console.log(this.dataset.mail + " quick-btn click!!");
            this.showUserModal(this.dataset.mail);
          });
        }
      });
    },
    async refreshMembers() {
      this.membersD1 = [];

      await Http.request({
        method: "POST",
        url: this.$API_URL + "/membersD1",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {"hideinactive" : this.hideinactive}
      })
        .then(({ data }) => {
          if (data.length) {
            this.membersD1 = data;
          } else {
            this.hasNoData = true;
          }
        })
        .catch((err) => {
          console.log(err);
          this.hasNoData = true;
        });
    },
  },
};
</script>
<style>
table td {
  padding: 0 !important;
  vertical-align: middle !important;
}
</style>