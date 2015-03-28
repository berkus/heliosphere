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
)

var tindex, _ = template.ParseFiles("templates/index.html", "templates/events.html")
var tevents, _ = template.ParseFiles("templates/events.html")

func initWeb() {
    router := mux.NewRouter()
    
    router.HandleFunc("/events", events).Methods("GET")
    router.HandleFunc("/events", add_event).Methods("POST")
    router.HandleFunc("/events/{id}", event).Methods("GET")
    router.HandleFunc("/events/{id}", delete_event).Methods("DELETE")

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

	  events, err := GetEvents(c, 1)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    grouping := make(map[string][]Event)

    for _, event := range events {
        rounded := stringify(event.Date.Truncate(24 * time.Hour))
        grouping[rounded] = append(grouping[rounded], event)
    }

    render(w, tindex, grouping)
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

    grouping := make(map[string][]Event)
    for _, event := range events {
        rounded := stringify(event.Date.Truncate(24 * time.Hour))
        grouping[rounded] = append(grouping[rounded], event)
    }

    render(w, tevents, grouping)
}

func delete_event(w http.ResponseWriter, r *http.Request) {
    c := appengine.NewContext(r)

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

    grouping := make(map[string][]Event)
    for _, event := range events {
        if event.Id != to_delete.Id {
            rounded := stringify(event.Date.Truncate(24 * time.Hour))
            grouping[rounded] = append(grouping[rounded], event)
        }
    }

    render(w, tevents, grouping)
}

func join(w http.ResponseWriter, r *http.Request) {
    fmt.Fprint(w, "hello, world")
}

func leave(w http.ResponseWriter, r *http.Request) {
    fmt.Fprint(w, "hello, world")
}