package heliosphere

import (
	"errors"
	"strconv"
	"time"

	"appengine/datastore"
)

type Player struct {
	Id        string
	FirstName string
	LastName  string
	PSNID     string
}

type Class int

const (
	Warlock Class = iota
	Hunter
	Titan
)

type Character struct {
	Player *datastore.Key
	Class  Class
	Level  int
}

type EventType int

const (
	Patrol EventType = iota
	Story
	Daily
	Weekly
	Nightfall
	Strikes
	VoG
	VoG_HM
	CE
	CE_HM
	Control
	Clash
	Salvage
	Skirmish
	Doubles
	Rumble
)

func ParseType(etype string) (EventType, error) {
	switch etype {
	case "Vault of Glass – Normal":
		return VoG, nil
	case "Vault of Glass – Hard":
		return VoG_HM, nil
	case "Crota's End – Normal":
		return CE, nil
	case "Crota's End – Hard":
		return CE_HM, nil
	case "Nightfall":
		return Nightfall, nil
	case "Weekly Heroic Strike":
		return Weekly, nil
	case "Daily Heroic Story":
		return Daily, nil
	case "Strike Playlist":
		return Strikes, nil
	case "Control":
		return Control, nil
	case "Clash":
		return Clash, nil
	case "Salvage":
		return Salvage, nil
	case "Skirmish":
		return Skirmish, nil
	case "Doubles Skirmish":
		return Doubles, nil
	case "Rumble":
		return Rumble, nil
	}
	return -1, errors.New("Unknown Event Type " + etype)
}

type Event struct {
	Id           int
	Type         EventType
	Date         time.Time
	Comments     string
	Participants []Participant
}

type EventsProto struct {
	Date   string
	Events []*EventProto
}

func (p *EventsProto) append(event *EventProto) {
	p.Events = append(p.Events, event)
}

type EventProto struct {
	Event         Event
	IsParticipant bool
	CanJoin       bool
}

func (e *Event) Name() string {
	switch e.Type {
	case VoG:
		return "Vault of Glass – Normal"
	case VoG_HM:
		return "Vault of Glass – Hard"
	case CE:
		return "Crota's End – Normal"
	case CE_HM:
		return "Crota's End – Hard"
	case Nightfall:
		return "Nightfall"
	case Weekly:
		return "Weekly Heroic Strike"
	case Daily:
		return "Daily Heroic Story"
	case Strikes:
		return "Strike Playlist"
	case Control:
		return "Control"
	case Clash:
		return "Clash"
	case Salvage:
		return "Salvage"
	case Skirmish:
		return "Skirmish"
	case Doubles:
		return "Doubles Skirmish"
	case Rumble:
		return "Rumble"
	}
	return "Unknown Event Type"
}

func (e *Event) Time() string {
	return e.Date.Format("15:04")
}

func (e *Event) Count() string {
	return strconv.Itoa(len(e.Participants)) + "/" + strconv.Itoa(e.Capacity())
}

func (e *Event) HasRoom() bool {
	return len(e.Participants) < e.Capacity()
}

func (e *Event) IsParticipant() bool {
	return true
}

func (e *Event) CanJoin() bool {
	return false
}

func (e *Event) Capacity() int {
	switch e.Type {
	case VoG:
		return 6
	case VoG_HM:
		return 6
	case CE:
		return 6
	case CE_HM:
		return 6
	case Nightfall:
		return 3
	case Weekly:
		return 3
	case Daily:
		return 3
	case Strikes:
		return 3
	case Control:
		return 6
	case Clash:
		return 6
	case Salvage:
		return 3
	case Skirmish:
		return 3
	case Doubles:
		return 3
	case Rumble:
		return 6
	}
	return -1
}

type ByDate []Event

func (a ByDate) Len() int           { return len(a) }
func (a ByDate) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByDate) Less(i, j int) bool { return a[i].Date.Before(a[j].Date) }

type Participant struct {
	Name string
}
