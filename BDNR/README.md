
# Proyecto final NoSQL2022

El objetivo del proyecto es demostrar conocimiento y capacidad de manejo de las bases de datos Neo4j, MongoDB y MonetDB. Para cumplir el cometido, utilizamos una API que contiene a todos los superhéroes de MARVEL con sus respectivos atributos como descripción, historias, eventos y cómics. A través de ETL's y manipulación de archivos, las insertamos a las bases de datos para su posterior análisis con queries. 


# Inserción a MongoDB -ETL
Para la inserción de todos los superhéroes, conectamos con la API de Marvel a través de un ETL que usa pymongo, requests y pandas con el objetivo de insertar un .json a MongoDB. 
El archivo se titula ETL y para hacer uso de este mismo, se debe de correr en Visual Studio Code o cualquier IDE de su preferencia que soporte Python.  

# Inserción a MonetDB

El ETL que prepara la información y el .csv es el mimso que se emplea en MongoDB.
En este caso, tenemos que seguir y correr línea a línea en la terminal el archivo insercion_en_monet. Primero se hace una copia al contenedor de Monet del .csv. Se hizo una base de datos desde el shell de MonetDB, con sus tablas, schemas y un copy offset que copia el .csv a la tabla. 

# Inserción a Neo4j

Para migrar a Neo4j, se deben de correr dos archivos. El ETL que prepara la información y el .csv para Neo4J es el mismo que utilizamos en MongoDB.   
El primero, se corre desde la terminal en bash. El archivo se titula insercion_en_neo4j1. 
El segundo se corre directo en el shell de Neo4J que soporta Cypher. El archivo se titula insercion_en_neo4j2.


## Queries - MongoDB
Numero de comics totales de los xmen:
```javascript
db.getCollection("marvel_superheroes").aggregate([
{$unwind:'$comics'},
{$match:{'name':{ $in: ['Wolverine','Charles Xavier','Cyclops','Beast','Cable','Iceman','Angel','Jean Grey']}}},
{$group:{_id:null,totalComics:{$sum:'$comics.available'}}}])
```

Promedio de comics por xmen:
```javascript
db.getCollection("marvel_superheroes").aggregate([
{$unwind:'$comics'},
{$match:{'name':{ $in: ['Wolverine','Charles Xavier','Cyclops','Beast','Cable','Iceman','Angel','Jean Grey']}}},
{$group:{_id:null,totalComics:{$avg:'$comics.available'}}}])
```

Series en las que thor aparece:
```javascript
db.getCollection("marvel_superheroes").aggregate([
{$unwind:'$comics.items'},
{$match:{'name':'Thor'}},
{$project:{"comics.items.name":1}}])
```


## Queries - Monetdb

Para los queries de MonetDB, nos cuestionamos lo siguiente:

¿Cuántos comics tiene el crew original de los avengers? ¿En qué percentil se sitúan? Siendo 1 el que más comics tiene y 0 el que menos tiene.
```sql
select hero, number_of_comics, percent_rank 
from (select ms.name as hero, ms.comics_available as Number_of_Comics, percent_rank() over (order by ms.comics_available asc) as percent_rank from marvel_superheroes ms order by ms.comics_available desc) as sbq1 
where hero in ('Hulk', 'Black Widow', 'Thor', 'Captain America', 'Iron Man', 'Hawkeye');
```
De manera general, estos son los números de comics que hay por héroe y su respectivo rank.
```sql
select ms.name as Hero, ms.comics_available as Number_of_Comics, percent_rank() over (order by ms.comics_available asc) as percent_rank 
from marvel_superheroes ms order by ms.comics_available desc;
```
¿Cuales son los top 10 superheroes que tienen más historias, eventos, comics y series asociadas a su nombre?

```sql
select ms.name, (ms.stories_available + ms.comics_available + ms.series_available + ms.events_available)/4 as average from marvel_superheroes ms order by average desc limit 10;
```

Del elenco principal de endgame, ¿quién está por abajo de la media de las columnas de historias, eventos, comics y series? Es decir, ¿a quién se les ha desarrollado menos su personaje?

```sql
select ms.name from marvel_superheroes ms where (ms.stories_available < (select avg(ms.stories_available) from marvel_superheroes ms) or ms.comics_available < (select avg(ms.comics_available) from marvel_superheroes ms) or ms.series_available < (select avg(ms.series_available) from marvel_superheroes ms) or ms.events_available < (select avg(ms.events_available) from marvel_superheroes ms)) and ms.name in ('Hulk', 'Black Widow', 'Thor', 'Captain America', 'Iron Man', 'Hawkeye', 'Groot', 'Ant-Man', 'Captain Marvel', 'Rocket Raccoon', 'Thanos', 'Okoye', 'Scarlet Witch', 'Winter Soldier', 'Loki', 'Falcon', 'Shuri', 'Mantis', 'Drax', 'Gamora', 'Star-Lord', 'Wasp', 'Nick Fury', 'Maria Hill', 'Nebula', 'Black Panther', 'Doctor Strange', 'Pepper Potts', 'The Ancient', 'Korg', 'Valkyrie', 'MBaku', 'Spider-Man', 'Ned Leeds', 'Peggy Carter', 'War Machine', 'Warsong');
```

## Queries - Neo4j

¿A cuáles eventos asisten los superhéroes de una determinada serie?
```cypher
MATCH (se:Serie)-->(:Superhero)-->(e:Event)
RETURN se.name as serieName, collect(distinct e.name)
```
¿Super héroe con más comics?
```cypher
MATCH (s:Superhero)-->(c:Comic)
WITH collect (DISTINCT c.name) AS comics, s.name as name, count(*) as cont
RETURN name, cont
ORDER BY cont desc
```

¿Qué evento junta más super héroes?
```cypher
MATCH (e:Event)-->(s:Superhero)
WITH collect (DISTINCT s.name) AS heroes, e.name as event_name, count(*) as cont
RETURN event_name, cont
ORDER BY cont desc
```
