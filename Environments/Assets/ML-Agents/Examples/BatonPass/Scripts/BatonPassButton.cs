using UnityEngine;
using Random = UnityEngine.Random;
using Unity.MLAgents;

public class BatonPassButton : MonoBehaviour
{
    public Material onMaterial;
    public Material offMaterial;
    public GameObject myButton;
    public GameObject AgentPrefab;
    public GameObject Food;
    public BatonPassArea Area;
    bool m_State;



    public bool GetState()
    {
        return m_State;
    }


    public void ResetSwitch()
    {
        m_State = false;
        tag = "switchOff";
        transform.rotation = Quaternion.Euler(0f, 0f, 0f);
        myButton.GetComponent<Renderer>().material = offMaterial;
        if (Random.Range(0f, 1f) < Academy.Instance.EnvironmentParameters.GetWithDefault("button_on_prob", 0f))
        {
            Activate(null);
        }
    }

    void OnCollisionEnter(Collision other)
    {
        if (other.gameObject.CompareTag("agent") && m_State == false)
        {
            var agent = other.gameObject.GetComponent<BatonPassAgent>();
            if (agent.CanPress)
            {
                Activate(other.gameObject);
                agent.CanPress = false;
            }
        }
    }

    public void SetActivated(){
        myButton.GetComponent<Renderer>().material = onMaterial;
        m_State = true;
        tag = "switchOn";
    }

    void Activate(GameObject pressingAgent)
    {
        SetActivated();
        SpawnAgent(pressingAgent);
        // pressingAgent.GetComponent<BatonPassAgent>().SetLife(50);
        Food.gameObject.SetActive(true);
    }

    void SpawnAgent(GameObject pressingAgent)
    {
        // if (pressingAgent != null)
        // {
        //     Area.UnregisterAgent(pressingAgent);
        //     Destroy(pressingAgent);
        //     var agent1 = GameObject.Instantiate(AgentPrefab, gameObject.transform.position + new Vector3(2 , 0, 0), default(Quaternion), Area.transform);
        //     // Area.AddReward(0f);
        //     Area.RegisterAgent(agent1);
        // }

        var agent2 = GameObject.Instantiate(AgentPrefab, gameObject.transform.position + new Vector3(3, 0, 0), default(Quaternion), Area.transform);
        // Area.AddReward(0f);
        Area.RegisterAgent(agent2);
    }
}
