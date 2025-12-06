CREATE TABLE circuits (
    circuitId       INT PRIMARY KEY,
    circuitRef      VARCHAR(100),
    name            VARCHAR(255),
    location        VARCHAR(255),
    country         VARCHAR(255),
    lat             FLOAT,
    lng             FLOAT,
    alt             INT
);

CREATE TABLE race (
    raceId      INT PRIMARY KEY,
    year        INT,
    round       INT,
    circuitId   INT,
    name        VARCHAR(255),
    date        DATE,
    time        VARCHAR(50),
    FOREIGN KEY (circuitId) REFERENCES circuits(circuitId)
);

CREATE TABLE constructors (
    constructorId   INT PRIMARY KEY,
    constructorRef  VARCHAR(100),
    name            VARCHAR(255),
    nationality     VARCHAR(255)
);

CREATE TABLE drivers (
    driverId    INT PRIMARY KEY,
    number      VARCHAR(10),
    code        VARCHAR(10),
    forename    VARCHAR(100),
    surname     VARCHAR(100),
    dob         DATE,
    nationality VARCHAR(100)
);

CREATE TABLE status (
    statusId    INT PRIMARY KEY,
    status      VARCHAR(255)
);

CREATE TABLE constructor_results (
    constructorResultsId INT PRIMARY KEY,
    raceId               INT,
    constructorId        INT,
    points               INT,
    FOREIGN KEY (raceId) REFERENCES race(raceId)
);

CREATE TABLE constructor_standings (
    raceId          INT,
    constructorId   INT,
    points          INT,
    position        INT,
    wins            INT,
    PRIMARY KEY (raceId, constructorId),
    FOREIGN KEY (constructorId) REFERENCES constructors(constructorId),
    FOREIGN KEY (raceId) REFERENCES race(raceId)
);

CREATE TABLE driver_standings (
    raceId      INT,
    driverId    INT,
    points      INT,
    position    INT,
    wins        INT,
    PRIMARY KEY (raceId, driverId),
    FOREIGN KEY (driverId) REFERENCES drivers(driverId),
    FOREIGN KEY (raceId) REFERENCES race(raceId)
);

CREATE TABLE lap (
    raceId          INT,
    driverId        INT,
    lapNumber       INT,
    currentPosition INT,
    time            VARCHAR(20),
    PRIMARY KEY (driverId, raceId, lapNumber),
    FOREIGN KEY (driverId) REFERENCES drivers(driverId),
    FOREIGN KEY (raceId) REFERENCES race(raceId)
);

CREATE TABLE pit_stops (
    raceId      INT,
    driverId    INT,
    stopNumber  INT,
    lapNumber   INT,
    timeOfStop  VARCHAR(20),
    duration    VARCHAR(20),
    PRIMARY KEY (raceId, driverId, stopNumber),
    FOREIGN KEY (driverId) REFERENCES drivers(driverId),
    FOREIGN KEY (raceId) REFERENCES race(raceId)
);

CREATE TABLE qualifying (
    qualifyId       INT,
    raceId          INT,
    driverId        INT,
    constructorId   INT,
    number          INT,
    position        INT,
    q1              VARCHAR(50),
    q2              VARCHAR(50),
    q3              VARCHAR(50),
    PRIMARY KEY (qualifyId, raceId, driverId, constructorId),
    FOREIGN KEY (constructorId) REFERENCES constructors(constructorId),
    FOREIGN KEY (driverId) REFERENCES drivers(driverId),
    FOREIGN KEY (raceId) REFERENCES race(raceId)
);

CREATE TABLE result (
    resultId        INT PRIMARY KEY,
    raceId          INT,
    driverId        INT,
    constructorId   INT,
    number          INT,
    grid            INT,
    position        VARCHAR(50),
    positionOrder   INT,
    points          INT,
    statusId        INT,
    FOREIGN KEY (constructorId) REFERENCES constructors(constructorId),
    FOREIGN KEY (driverId) REFERENCES drivers(driverId),
    FOREIGN KEY (raceId) REFERENCES race(raceId),
    FOREIGN KEY (statusId) REFERENCES status(statusId)
);