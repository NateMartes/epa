import {React, useState, useEffect} from 'react';
import {View, FlatList, StyleSheet, Text, StatusBar} from 'react-native';
import {SafeAreaView, SafeAreaProvider} from 'react-native-safe-area-context';
export default function Scrollable(){
const [data, setData] = useState(null);
let pageNo = 0
const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginTop: StatusBar.currentHeight || 0,
  },
  item: {
    backgroundColor: '#f9c2ff',
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
  },
  title: {
    fontSize: 32,
  },
  text: {
    fontSize: 16
  }
});


const getData = async () => {
   const response = await fetch("https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/auth/post", {
   	 method: 'GET',headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session_token}` }, body: substring, });
  const responseJson = response.json();
  const data = responseJson;
  console.log(data);
  setData(data);
};


useEffect(() => {
    getData();
  }, []);
//type ItemProps = {title: string, content: string, created_by: string, category: string };

const getMoreData = async () => {
         const response = await fetch("https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/auth/post", {
   	 method: 'POST',headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session_token}` }, body: substring, });
  	 const responseJson = response.json();
  	 const newData = responseJson;
      setItems((data) => [...data, ...newData]);
};
const Item = ({title , content, category, created_by }) => (
  <View style={styles.item}>
    <Text style={styles.title}>{title}</Text>
    <Text style={styles.text}> {content} </Text>
    <Text style={styles.text}>  {category} {created_by} </Text>
    
  </View>
);

  const renderItem = ({ item, index }) => (
    <Item description={item.description} title={item.title} category={item.category} created_by={item.created_by}/>
  );

return(
  <SafeAreaProvider>
    <SafeAreaView style={styles.container}>
      <FlatList
        data={data}
        renderItem={renderItem}
        keyExtractor={item => item.id}
	onEndReachedThreshold={0.2} 
//	onEndReached{({ distanceFromEnd }) => {
//		if (distanceFromEnd < 0) return;
//		if (loading) return;
//		getMoreData();
//	}	
      />
    </SafeAreaView>
  </SafeAreaProvider>
);


}