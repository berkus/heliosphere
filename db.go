package heliosphere

import (
	"errors"
	"time"

	"appengine"
	"appengine/datastore"
)

type Counter struct {
	Count int
}

func NewEvent(c appengine.Context, etype EventType, date time.Time, comments string) (*Event, error) {
	id, err := Increment(c, "Event")
	if err != nil {
		return nil, err
	}

	event := Event{
		Id:       id,
		Type:     etype,
		Date:     date,
		Comments: comments,
	}

	key := datastore.NewIncompleteKey(c, "Event", nil)
	_, err = datastore.Put(c, key, &event)

	return &event, err
}

func RemoveEvent(c appengine.Context, event *Event) error {
	q := datastore.NewQuery("Event").Filter("Id =", event.Id).Limit(1).KeysOnly()
	events, err := q.GetAll(c, nil)
	if err != nil {
		return err
	}
	if len(events) != 1 {
		return errors.New("Event not found")
	}
	err = datastore.Delete(c, events[0])
	return err
}

func GetEvent(c appengine.Context, id int) (*Event, error) {
	q := datastore.NewQuery("Event").Filter("Id =", id).Limit(1)
	var events []Event
	_, err := q.GetAll(c, &events)
	if err != nil {
		return nil, err
	}
	if len(events) != 1 {
		return nil, errors.New("Event not found")
	}
	return &events[0], nil
}

func GetEvents(c appengine.Context, page int) ([]Event, error) {
	q := datastore.NewQuery("Event").Filter("Date >=", time.Now().Add(time.Hour)).Order("Date").Limit(10).Offset(10 * (page - 1))
	var events []Event
	_, err := q.GetAll(c, &events)
	return events, err
}

func GetPlayer(c appengine.Context, id string) (*Player, error) {
	q := datastore.NewQuery("Player").Filter("Id =", id).Limit(1)
	var events []Player
	_, err := q.GetAll(c, &events)
	if err != nil {
		return nil, err
	}
	if len(events) != 1 {
		return nil, errors.New("Player not found")
	}
	return &events[0], nil
}

func AddParticipant(c appengine.Context, id int, player *Player) (*Event, error) {
	q := datastore.NewQuery("Event").Filter("Id =", id).Limit(1)
	var events []Event
	keys, err := q.GetAll(c, &events)
	if err != nil {
		return nil, err
	}
	if len(events) != 1 {
		return nil, errors.New("Event not found")
	}
	event := &events[0]

	event.Participants = append(event.Participants, Participant{Name: player.PSNID})

	_, err2 := datastore.Put(c, keys[0], event)

	return event, err2
}

func RemoveParticipant(c appengine.Context, id int, player *Player) (*Event, error) {
	q := datastore.NewQuery("Event").Filter("Id =", id).Limit(1)
	var events []Event
	keys, err := q.GetAll(c, &events)
	if err != nil {
		return nil, err
	}
	if len(events) != 1 {
		return nil, errors.New("Event not found")
	}
	event := &events[0]

	ps := make([]Participant, 0, len(event.Participants))
	for _, participant := range event.Participants {
		if participant.Name != player.PSNID {
			ps = append(ps, participant)
		}
	}
	event.Participants = ps

	_, err2 := datastore.Put(c, keys[0], event)

	return event, err2
}

func NewPlayer(c appengine.Context, id string, first string, last string, psnid string) (*Player, error) {
	player := Player{
		Id:        id,
		FirstName: first,
		LastName:  last,
		PSNID:     psnid,
	}

	key := datastore.NewIncompleteKey(c, "Player", nil)
	_, err := datastore.Put(c, key, &player)

	return &player, err
}

func inc(c appengine.Context, key *datastore.Key) (int, error) {
	var x Counter
	if err := datastore.Get(c, key, &x); err != nil && err != datastore.ErrNoSuchEntity {
		return 0, err
	}
	x.Count++
	if _, err := datastore.Put(c, key, &x); err != nil {
		return 0, err
	}
	return x.Count, nil
}

func Increment(c appengine.Context, model string) (int, error) {
	var count int
	err := datastore.RunInTransaction(c, func(c appengine.Context) error {
		var err1 error
		count, err1 = inc(c, datastore.NewKey(c, "Counter", model, 0, nil))
		return err1
	}, nil)
	if err != nil {
		return 0, err
	}
	return count, err
}
