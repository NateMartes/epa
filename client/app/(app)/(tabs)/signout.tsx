import { Text, View, StyleSheet } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link, useRouter } from 'expo-router';
import Button from '@/components/Button';
import Input from '@/components/Input';
import AsyncStorage from '@react-native-async-storage/async-storage';


export default function Index() {
  const router = useRouter();
  const removeData = async () => {
    try {
     await AsyncStorage.setItem('sessionID', null);
        } catch (e) {}
	router.navigate('/login');
  };
  return (
    <SafeAreaView style={styles.container}>
      <Button label="Sign out" onPress={removeData}/>
      <View style={styles.space}/>
      <View style={styles.link}>
      <Link href="/index" style={styles.button}>
        Create Post
      </Link>
      <Link href="/about" style={styles.button}>
        Make Posts (links to about rn)
      </Link>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#00000f',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: '#eee',
  },
  button: {
    fontSize: 15,
    textDecorationLine: 'underLine',
    color: '#ccc',
  },
  poster: {
    flex: 1,
    height: '100%',
    width: '100%',
    justifyContent:'center',
    alignItems: 'center',
  },
  link: {
    justifyContent: 'flex-end',
    },
  space: {
    flex: 1/3,
    },
    
});