DROP DATABASE IF EXISTS walk_with_me;

CREATE DATABASE walk_with_me
  DEFAULT COLLATE utf8_general_ci;
USE walk_with_me;

CREATE TABLE user (
  user_id int(10) unsigned NOT NULL AUTO_INCREMENT, 
  user_email varchar(50) NOT NULL,
  user_name varchar(20) NOT NULL,
  pass_hash char(60) NOT NULL,
  age tinyint(2) unsigned DEFAULT 0,
  gender enum('M','F') DEFAULT 'M',
  
  PRIMARY KEY(user_id),
  INDEX(user_email,user_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE location (
  loc_id int(10) unsigned NOT NULL AUTO_INCREMENT,
  latitude float(10,6) NOT NULL,
  longitude float(10,6) NOT NULL,

  PRIMARY KEY(loc_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE spot (
  spot_id int(10) unsigned NOT NULL AUTO_INCREMENT,
  spot_name varchar(50) NOT NULL,
  spot_type enum('sight','facility','restaurant','entertainment','other') NOT NULL,
  is_official tinyint(1) NOT NULL,
  loc_id int(10) unsigned NOT NULL,
  description varchar(255) DEFAULT NULL,
  user_id int(10) unsigned DEFAULT NULL,
  proposed_date date DEFAULT NULL,
 
  PRIMARY KEY(spot_id),
  FOREIGN KEY(user_id)
    REFERENCES user(user_id),
  FOREIGN KEY(loc_id)
    REFERENCES location(loc_id),
  INDEX(user_id,loc_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE review (
  review_id int(10) unsigned NOT NULL AUTO_INCREMENT,
  user_id int(10) unsigned NOT NULL,
  spot_id int(10) unsigned NOT NULL,
  review_date date NOT NULL,
  review_contents varchar(255) DEFAULT NULL,
  rating enum('1','2','3','4','5') DEFAULT '5',
 
  PRIMARY KEY(review_id),
  FOREIGN KEY(user_id)
    REFERENCES user(user_id),
  FOREIGN KEY(spot_id)
    REFERENCES spot(spot_id),
  INDEX(spot_id,user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE plan (
  route_id int(10) unsigned NOT NULL AUTO_INCREMENT,
  user_id int(10) unsigned NOT NULL,
  source_id int(10) unsigned NOT NULL,
  destination_id int(10) unsigned NOT NULL,
  distance float NOT NULL,
  duration int NOT NULL,
  air_pollution_level enum('L','M','H','U') DEFAULT 'U',
  transportation enum('walk','run','cycle') NOT NULL,
  is_oneway tinyint(1) NOT NULL,
  fixed_duration tinyint(1) NOT NULL, 
  
  PRIMARY KEY(route_id),
  FOREIGN KEY(user_id)
    REFERENCES user(user_id),
  FOREIGN KEY(source_id)
    REFERENCES location(loc_id),
  FOREIGN KEY(destination_id)
    REFERENCES location(loc_id),
  INDEX(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE route_list (
  route_id int(10) unsigned NOT NULL,
  spot_id int(10) unsigned NOT NULL,
  
  PRIMARY KEY(route_id,spot_id),
  FOREIGN KEY(route_id)
    REFERENCES plan(route_id),
  FOREIGN KEY(spot_id)
    REFERENCES spot(spot_id),
  INDEX(route_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TRIGGER set_spot_proposed_date BEFORE INSERT
    ON spot FOR EACH ROW SET NEW.proposed_date = NOW();
  
CREATE TRIGGER set_review_date BEFORE INSERT
    ON review FOR EACH ROW SET NEW.review_date = NOW();


USE mysql;

GRANT ALL PRIVILEGES ON *.* TO 'walkwithme'@'localhost' IDENTIFIED BY PASSWORD '*FFF9DA0267AD5AFA60004128E93B3C60A7FF9188' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `walk_with_me`.* TO 'walkwithme'@'localhost' WITH GRANT OPTION;
