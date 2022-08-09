CREATE DATABASE IF NOT EXISTS Forest;

CREATE TABLE IF NOT EXISTS Individual (
    individual_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    password VARCHAR(60) NOT NULL,
    filename VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Organization (
    organization_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    password VARCHAR(60) NOT NULL,
    filename VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    owner INT NOT NULL,
    event_name VARCHAR(30) NOT NULL,
    event_description VARCHAR(50) NOT NULL,
    number_of_participants INT NOT NULL,
    number_of_seeds INT NOT NULL,
    venue VARCHAR(30) NOT NULL,
  	seedling VARCHAR(30) NOT NULL,
    cost INT NOT NULL,
    start_date VARCHAR(20) NOT NULL,
  	end_date VARCHAR(20) NOT NULL,
    event_status VARCHAR(20) NOT NULL DEFAULT 'Active',
    rating FLOAT(3, 2) NOT NULL,
    FOREIGN KEY (owner) REFERENCES Organization (organization_id)
);

CREATE TABLE Participation (
	participation_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    individual_id INT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES Events (event_id),
    FOREIGN KEY (individual_id) REFERENCES Individual (individual_id)
);

CREATE TABLE IF NOT EXISTS Rating (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    individual_id INT NOT NULL,
    event_id INT NOT NULL,
    rating_review TEXT NOT NULL,
    rating_rating INT NOT NULL,
    rating_date DATE NOT NULL,
    FOREIGN KEY (individual_id) REFERENCES Individual (individual_id),
    FOREIGN KEY (event_id) REFERENCES Events (event_id)
);