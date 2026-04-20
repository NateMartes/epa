import {React, useState, useEffect} from 'react';
import {View, FlatList, StyleSheet, Text, StatusBar} from 'react-native';
import {SafeAreaView, SafeAreaProvider} from 'react-native-safe-area-context';
export default function Scrollable(){
const [data, setData] = useState(null);

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
  const resp = await fetch("https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/post");
  const data = await resp.json();
  console.log(data);
  setData(data);
};


useEffect(() => {
    getData();
  }, []);
//type ItemProps = {title: string, content: string, created_by: string, category: string };

const getMoreData = async () => {
      const response = await fetch(api);
      const newData = await response.json();

      setItems((prevItems) => [...prevItems, ...newData]);
};
const Item = ({title , content }) => (
  <View style={styles.item}>
    <Text style={styles.title}>{title}</Text>
    <Text style={styles.text}> {content} </Text>
  </View>
);

return(
  <SafeAreaProvider>
    <SafeAreaView style={styles.container}>
      <FlatList
        data={data}
        renderItem={({item}) => <Item title={item.title} Item body={item.body} />}
        keyExtractor={item => item.id}
	onEndReachedThreshold={0.2} 
//	onEndReached{({ distanceFromEnd }) => {
//		if (distanceFromEnd < 0) return;
//		getMoreData();
//	}	
      />
    </SafeAreaView>
  </SafeAreaProvider>
);


}