CREATE TABLE Summoners (
	account_id VARCHAR(56) PRIMARY KEY,
	summoner_name VARCHAR(30)
);

CREATE TABLE SummonerMatches (
	account_id VARCHAR(56),
	game_id BIGINT,
	match_timestamp BIGINT,
	queue INT,
	season INT,
	duration SMALLINT,
	win BOOLEAN,
	champion VARCHAR(15),
	kills SMALLINT,
	deaths SMALLINT,
	assists SMALLINT,
	gold_earned INT,
	champion_damage INT,
	objective_damage INT,
	damage_healed INT,
	vision_score SMALLINT,
	control_wards_purchased SMALLINT,
	minions_killed INT,
	neutral_monsters_killed INT,
	FOREIGN KEY (account_id) REFERENCES Summoners(account_id),
	PRIMARY KEY (account_id, game_id)
);