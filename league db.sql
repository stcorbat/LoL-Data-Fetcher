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


CREATE PROCEDURE cspm (
    p_account_id VARCHAR(56),
    p_queue SMALLINT,
    p_timestamp BIGINT
)
BEGIN
    SELECT avg((minions_killed + neutral_monsters_killed) / duration * 60) as stat, count(*) as amount
    FROM SummonerMatches
    WHERE account_id = p_account_id AND queue = p_queue AND match_timestamp >= p_timestamp;
END//


CREATE PROCEDURE win_rate (
    p_account_id VARCHAR(56),
    p_queue SMALLINT,
    p_timestamp BIGINT
)
BEGIN
    SELECT avg(win) as stat, count(*) as amount
    FROM SummonerMatches
    WHERE account_id = p_account_id AND queue = p_queue AND match_timestamp >= p_timestamp;
END//


CREATE PROCEDURE cspm_by_champ (
    p_account_id VARCHAR(56),
    p_queue SMALLINT,
    p_timestamp BIGINT
)
BEGIN
    SELECT champion, avg((minions_killed + neutral_monsters_killed) / duration * 60) as stat, count(*) as amount
    FROM SummonerMatches
    WHERE account_id = p_account_id AND queue = p_queue AND match_timestamp >= p_timestamp
    GROUP BY champion
    ORDER BY amount DESC;
END//


CREATE PROCEDURE win_rate_by_champ (
    p_account_id VARCHAR(56),
    p_queue SMALLINT,
    p_timestamp BIGINT
)
BEGIN
    SELECT champion, avg(win) as stat, count(*) as amount
    FROM SummonerMatches
    WHERE account_id = p_account_id AND queue = p_queue AND match_timestamp >= p_timestamp
    GROUP BY champion
    ORDER BY amount DESC;
END//