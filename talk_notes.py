import argparse
import click
import pickle
import datetime
import os
import subprocess
import time

parser = argparse.ArgumentParser()

class Talk:
    def __init__(self, id, date=None):
        if date is None:
            self.date = datetime.date.today()
        self.filename = None
        self.title = None
        self.venue = None
        self.id = id
    
    def print_info(self):
        dateStr = self.date.__str__()
        if self.title is None:
            titleStr = 'Untitled'
        else:
            titleStr = self.title
        if self.venue is None:
            print('{}: {} -- "{}"'.format(self.id, dateStr, titleStr))
        else: 
            print('{}: {} at {} -- "{}"'.format(self.id, dateStr, self.venue, titleStr))                 

class Person:
    def __init__(self, name, id, folderName, role=None):
        self.name = name
        self.id = id
        self.role = role
        self.pastRoles = []
        self.talks = []
        self.numTalks = 0
        self.folderName = folderName
        
    def update_role(self, newRole, moveCurrentRole=True):
        if moveCurrentRole and self.role is not None:
            self.pastRoles.append(self.role)
        self.role = newRole
        
    def edit_talk(self, talkId, databasePath, isNewTalk=False):
        talk = self.talks[talkId]
        if isNewTalk:
            currentYear = datetime.date.today().year
            currentMonth = datetime.date.today().month
            currentDay = datetime.date.today().day
            defaultText = 'Year: {}, month: {}, day: {};\nTitle:\nVenue:\nNotes:'.format(currentYear, currentMonth, currentDay)
            returnedText = click.edit(text=defaultText)
        else:
            filename = os.path.join(databasePath, self.folderName, '{}.txt'.format(talkId))
            click.edit(filename=filename)
            with open(filename, 'r') as f:
                returnedText = f.read()
        try:
            yearString = returnedText.partition('Year:')[2].partition(',')[0].strip()
            year = int(yearString)
            monthString = returnedText.partition('month:')[2].partition(',')[0].strip()
            month = int(monthString)
            dayString = returnedText.partition('day:')[2].partition(';')[0].strip()
            day = int(dayString)
            talkDate = datetime.date(year, month, day)
        except:
            print("Error parsing date information, using today's date")
            talkDate = datetime.date.today()
        try:
            titleString = returnedText.partition('Title:')[2].partition('\n')[0].strip()
            if len(titleString) == 0:
                title = None
            else:
                title = titleString
        except:
            print("Error parsing talk title")
            title = None            
        try:
            venueString = returnedText.partition('Venue:')[2].partition('\n')[0].strip()
            if len(venueString) == 0:
                venue = None
            else:
                venue = venueString
        except:
            print("Error parsing talk venue")
            venue = None
        
        if isNewTalk:
            try: 
                fileName = '{}.txt'.format(talk.id)
                pathUsed = os.path.join(databasePath, self.folderName, fileName)
                with open(pathUsed, 'w') as f:      
                    f.write(returnedText)
                print('Successfully saved talk information to {}'.format(pathUsed))
            except:
                secondsSinceEpoch = int(time.mktime(time.localtime()))
                try:
                    pathUsed = os.path.join(databasePath, '{}.txt'.format(secondsSinceEpoch))
                    with open(pathUsed, 'w') as f:
                        f.write(returnedText)
                except:
                    pathUsed = '{}.txt'.format(secondsSinceEpoch)
                    with open(pathUsed, 'w') as f:
                        f.write(returnedText)
                print('Error saving talk file, please check entry saved at {} and try again'.format(pathUsed))   
                
        talk.title = title
        talk.venue = venue
        talk.date = talkDate

        
    def add_talk(self, databasePath):
        if not os.path.isdir(os.path.join(databasePath, self.folderName)):
            os.mkdir(os.path.join(databasePath, self.folderName))
        newTalk = Talk(self.numTalks)
        self.numTalks += 1
        self.talks.append(newTalk)
        self.edit_talk(newTalk.id, databasePath, isNewTalk=True)
        
            
class Role:
    def __init__(self, title=None, institution=None):
        self.title = title
        self.institution = institution
        
        
class Metadata:
    def __init__(self, people = [], nameDict={}):
        self.people = []
        self.nameDict = nameDict
        self.numPeople = len(self.people)
        
    # TODO: check case where 2 different people may have the same name
    def add_person(self, name):
        newId = self.numPeople
        safeName = name.replace(' ', '_')
        newPerson = Person(name, newId, safeName)
        self.numPeople += 1
        self.people.append(newPerson)
        allNames = name.split(' ')
        for newName in allNames:
            if newName in self.nameDict:
                self.nameDict[newName].append(newId)
            else:
                self.nameDict[newName] = [newId]
        return newPerson
                
    def search_name(self, names):
        idsReturned = []
        for name in names:
            if name in self.nameDict:
                ids = self.nameDict[name]
                for id in ids:
                    if id not in idsReturned:
                        person = self.people[id]
                        print('{}: {}'.format(id, person.name.title()))
                    idsReturned.append(id)
        if len(idsReturned) == 0:
            print('Name not found')
    
def load_metadata(metadataFile):
    try:
        with open(metadataFile, 'rb') as f:
            metadata = pickle.load(f)
    except OSError:
        metadata = Metadata()
        print('No metadata file found, starting with an empty dictionary.')
    return metadata
        
def save_metadata(metadataFile, metadata):
    tempFile = metadataFile.replace('.', '_temp.')
    if os.path.exists(metadataFile):
        os.replace(metadataFile, tempFile)
    try:
        with open(metadataFile, 'wb') as f:
            pickle.dump(metadata, f)
    except:
        print('Error saving metadata, old metadata is saved at {}'.format(tempFile))

def check_existence(personId, talkId=None):
    try:
        person = metadata.people[personId]
    except:
        print('No person with id {} exists in this database'.format(personId))
        quit()
    if talkId is not None:
        try:
            talk = person.talks[talkId]
        except:
            print("Person {} ({}) doesn't have talk {}".format(personId, person.name.title(), talkId))
            quit()
    return person
        
parser = argparse.ArgumentParser()
parser.add_argument('metadataPath', help='Path to the pickle file that contains metadata about all talks')
parser.add_argument('databasePath', help='Path to the root folder where all talk note files are stored')
commandOptions = parser.add_mutually_exclusive_group()
commandOptions.add_argument('-n', '--newPerson', help='Add new person named <name>', metavar='<name>')
commandOptions.add_argument('-a', '--addTalk', type=int, help='Add talk to person <id>', metavar='<id>')
commandOptions.add_argument('-i', '--printInfo', type=int, help='Print info about and list talks by person <id>', metavar='<id>')
commandOptions.add_argument('-e', '--editTalk', type=int, nargs=2, help='Edit notes for talk <talk_id> by person <person_id>', metavar=('<person_id>', '<talk_id>'))
commandOptions.add_argument('-u', '--updateRole', nargs=2, help='Update the job or role for person <person_id>', metavar=('<person_id>', '<newRole>'))
commandOptions.add_argument('-s', '--search', help='Search for people named <name>', metavar='<name>')
args = parser.parse_args()

metadata = load_metadata(args.metadataPath)
databasePath = args.databasePath
if not os.path.exists(databasePath):
    print('No notes database found, creating directory {}'.format(databasePath))
    os.mkdir(databasePath)

if args.newPerson is not None:
    newPerson = metadata.add_person(args.newPerson.lower())
    save_metadata(args.metadataPath, metadata)
    print('Succesfully added {} to the database. Their ID is {}'.format(args.newPerson, newPerson.id))
elif args.addTalk is not None:
    personId = args.addTalk
    person = check_existence(personId)
    person.add_talk(databasePath)
    save_metadata(args.metadataPath, metadata)
    print('Succesfully added a talk for {} ({}) to the database (talk id = {}).'.format(personId, person.name.title(), person.numTalks-1))
elif args.printInfo is not None:
    personId = args.printInfo
    person = check_existence(personId)
    print('Name: {} (id={})'.format(person.name.title(), personId))
    if person.role is not None:
        print('Role: {}'.format(person.role))
    for pastRole in person.pastRoles:
        print('Previous role: {}'.format(pastRole))
    print('Talks in notes database:')
    for talk in person.talks:
        talk.print_info()
elif args.editTalk is not None:
    (personId, talkId) = args.editTalk
    person = check_existence(personId, talkId=talkId)
    person.edit_talk(talkId, databasePath)
    save_metadata(args.metadataPath, metadata)
    print('Successfully edited talk {} for {} ({}).'.format(talkId, person.id, person.name.title()))
elif args.updateRole is not None:
    (personId, newRole) = args.updateRole
    personId = int(personId)
    person = check_existence(personId)
    person.update_role(newRole)
    save_metadata(args.metadataPath, metadata)
    print('Successfully updated the role for {} ({})'.format(person.id, person.name.title()))
elif args.search is not None:
    namesToSearch = args.search.lower().split() # lowercase and split first and last (and etc) names
    metadata.search_name(namesToSearch)