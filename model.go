package heliosphere

import (
    "time"
    "errors"

    "appengine/datastore"
)

type Player struct {
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
        case "Vault of Glass – Normal": return VoG, nil
        case "Vault of Glass – Hard": return VoG_HM, nil
        case "Crota's End – Normal": return CE, nil
        case "Crota's End – Hard": return CE_HM, nil
        case "Nightfall": return Nightfall, nil
        case "Weekly Heroic Strike": return Weekly, nil
        case "Daily Heroic Story": return Daily, nil
        case "Strike Playlist": return Strikes, nil
        case "Control": return Control, nil
        case "Clash": return Clash, nil
        case "Salvage": return Salvage, nil
        case "Skirmish": return Skirmish, nil
        case "Doubles Skirmish": return Doubles, nil
        case "Rumble": return Rumble, nil
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

type Participant struct {
    Event     *datastore.Key
	Player    *datastore.Key
	Character *datastore.Key
}
