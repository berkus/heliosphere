package heliosphere

import (
    "fmt"
    "time"
    "sort"
    "strings"
    "strconv"
    "net/http"
    "html/template"
	
    "github.com/gorilla/mux"

    "appengine"
    "appengine/user"
)

var tindex, _ = template.ParseFiles("templates/index.html", "templates/events.html")
var tevents, _ = template.ParseFiles("templates/events.html")
var tplayer, _ = template.ParseFiles("templates/player.html")

func initWeb() {
    router := mux.NewRouter()
    
    router.HandleFunc("/events", events).Methods("GET")
    router.HandleFunc("/events", add_event).Methods("POST")
    router.HandleFunc("/events/{id}", event).Methods("GET")
    router.HandleFunc("/events/{id}", delete_event).Methods("DELETE")
    router.HandleFunc("/events/{id}/_join", join_event).Methods("POST")
    router.HandleFunc("/events/{id}/_leave", leave_event).Methods("POST")

    router.HandleFunc("/players/new", add_player_form).Methods("GET")
    router.HandleFunc("/players", add_player).Methods("POST")

    http.Handle("/", router)
}

func render(w http.ResponseWriter, tmpl *template.Template, data interface{}) {
    err := tmpl.Execute(w, data)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
}

func event(w http.ResponseWriter, r *http.Request) {
    c := appengine.NewContext(r)

    vars := mux.Vars(r)
    id, err := strconv.Atoi(vars["id"])
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    event, err := GetEvent(c, id)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    fmt.Fprint(w, event.Type)
}

func events(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)

    player, _ := GetPlayer(c, user.Current(c).ID)
    if player == nil {
        http.Redirect(w, r, "/players/new", http.StatusFound)
        return
    }

	events, err := GetEvents(c, 1)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    grouping := make(map[string][]EventProto)

    for _, event := range events {
        rounded := stringify(event.Date.Truncate(24 * time.Hour))
        grouping[rounded] = append(grouping[rounded], proto(event, player))
    }

    render(w, tindex, grouping)
}

func proto(event Event, player *Player) (EventProto) {
    participating := false
    for _, participant := range event.Participants {
        if player.PSNID == participant.Name {
            participating = true
            break
        }
    }
    can_join := !participating && event.HasRoom()
    return EventProto{Event: &event, IsParticipant: participating, CanJoin: can_join}
}

func stringify(t time.Time) string {
    const layout = "January, 2"
    today := time.Now().Truncate(24 * time.Hour)
    if t.UnixNano() == today.UnixNano() {
        return "Today"
    } else if t.UnixNano() == today.Add(24 * time.Hour).UnixNano() {
        return "Tomorrow"
    } else {
        return t.Format(layout)
    }
}

func add_event(w http.ResponseWriter, r *http.Request) {
    c := appengine.NewContext(r)

    player, _ := GetPlayer(c, user.Current(c).ID)

    err := r.ParseForm()
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    etype, err2 := ParseType(strings.TrimSpace(r.PostFormValue("etype")))
    if err2 != nil {
        http.Error(w, err2.Error(), http.StatusBadRequest)
        return
    }

    edate := strings.TrimSpace(r.PostFormValue("date"))
    etime := strings.TrimSpace(r.PostFormValue("time"))

    const layout = "01/02/2006 15:04"
    date, err3 := time.Parse(layout, edate + " " + etime)
    if err3 != nil {
        http.Error(w, err3.Error(), http.StatusBadRequest)
        return
    }

    comments := strings.TrimSpace(r.PostFormValue("comments"))

    event, err4 := NewEvent(c, etype, date, comments)
    if err4 != nil {
        http.Error(w, err4.Error(), http.StatusInternalServerError)
        return
    }
    
    events, err5 := GetEvents(c, 1)
    if err5 != nil {
        http.Error(w, err4.Error(), http.StatusInternalServerError)
        return
    }

    events = append(events, *event)
    sort.Sort(ByDate(events))

    grouping := make(map[string][]EventProto)
    for _, event := range events {
        rounded := stringify(event.Date.Truncate(24 * time.Hour))
        grouping[rounded] = append(grouping[rounded], proto(event, player))
    }

    render(w, tevents, grouping)
}

func delete_event(w http.ResponseWriter, r *http.Request) {
    c := appengine.NewContext(r)

    player, _ := GetPlayer(c, user.Current(c).ID)

    vars := mux.Vars(r)
    id, err := strconv.Atoi(vars["id"])
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    to_delete, err2 := GetEvent(c, id)
    if err2 != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    
    err3 := RemoveEvent(c, to_delete)
    if err3 != nil {
        http.Error(w, err3.Error(), http.StatusInternalServerError)
        return
    }

    events, err4 := GetEvents(c, 1)
    if err != nil {
        http.Error(w, err4.Error(), http.StatusInternalServerError)
        return
    }

    sort.Sort(ByDate(events))

    grouping := make(map[string][]EventProto)
    for _, event := range events {
        if event.Id != to_delete.Id {
            rounded := stringify(event.Date.Truncate(24 * time.Hour))
            grouping[rounded] = append(grouping[rounded], proto(event, player))
        }
    }

    render(w, tevents, grouping)
}

func join_event(w http.ResponseWriter, r *http.Request) {
    c := appengine.NewContext(r)

    player, _ := GetPlayer(c, user.Current(c).ID)

    err := r.ParseForm()
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    vars := mux.Vars(r)
    id, err := strconv.Atoi(vars["id"])
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    event, err := AddParticipant(c, id, player)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    events, err2 := GetEvents(c, 1)
    if err2 != nil {
        http.Error(w, err2.Error(), http.StatusInternalServerError)
        return
    }

    grouping := make(map[string][]EventProto)
    for _, e := range events {
        if e.Id == event.Id {
            rounded := stringify(event.Date.Truncate(24 * time.Hour))
            grouping[rounded] = append(grouping[rounded], proto(*event, player))
        } else {
            rounded := stringify(e.Date.Truncate(24 * time.Hour))
            grouping[rounded] = append(grouping[rounded], proto(e, player))
        }
    }

    render(w, tevents, grouping)
}

func leave_event(w http.ResponseWriter, r *http.Request) {
    c := appengine.NewContext(r)

    player, _ := GetPlayer(c, user.Current(c).ID)

    err := r.ParseForm()
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    vars := mux.Vars(r)
    id, err := strconv.Atoi(vars["id"])
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    event, err := RemoveParticipant(c, id, player)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    events, err2 := GetEvents(c, 1)
    if err2 != nil {
        http.Error(w, err2.Error(), http.StatusInternalServerError)
        return
    }

    grouping := make(map[string][]EventProto)
    for _, e := range events {
        if e.Id == event.Id {
            rounded := stringify(event.Date.Truncate(24 * time.Hour))
            grouping[rounded] = append(grouping[rounded], proto(*event, player))
        } else {
            rounded := stringify(e.Date.Truncate(24 * time.Hour))
            grouping[rounded] = append(grouping[rounded], proto(e, player))
        }
    }

    render(w, tevents, grouping)
}

func add_player_form(w http.ResponseWriter, r *http.Request) {
    render(w, tplayer, nil)
}

func add_player(w http.ResponseWriter, r *http.Request) {
    c := appengine.NewContext(r)

    err := r.ParseForm()
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    first := strings.TrimSpace(r.PostFormValue("first"))
    last := strings.TrimSpace(r.PostFormValue("last"))
    psnid := strings.TrimSpace(r.PostFormValue("psnid"))

    _, err2 := NewPlayer(c, user.Current(c).ID, first, last, psnid)
    if err2 != nil {
        http.Error(w, err2.Error(), http.StatusInternalServerError)
        return
    }
    http.Redirect(w, r, "/events", http.StatusFound)
}
