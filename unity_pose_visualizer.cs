/*
Unity C# Script to visualize poses with Mixamo character
Place this script on your character GameObject in Unity

Steps:
1. Import Mixamo character from https://www.mixamo.com/
2. Create empty GameObject and attach this script
3. Assign character's Animator component
4. Load your generated_poses.json file
5. Press Play to see animation

This creates smooth, realistic human animations from your pose data
*/

using UnityEngine;
using System.Collections.Generic;
using System.IO;

[System.Serializable]
public class PoseData
{
    public string video_path;
    public int seed_frames;
    public int generated_frames;
    public int total_frames;
    public int pose_dimension;
    public List<List<float>> poses;
}

public class PoseVisualizer : MonoBehaviour
{
    [Header("Settings")]
    public string jsonFilePath = "generated_poses.json";
    public Animator characterAnimator;
    public float frameRate = 30f;
    
    [Header("Joint Mapping")]
    public Transform hipJoint;
    public Transform spineJoint;
    public Transform leftShoulderJoint;
    public Transform rightShoulderJoint;
    public Transform leftElbowJoint;
    public Transform rightElbowJoint;
    public Transform leftKneeJoint;
    public Transform rightKneeJoint;
    
    private PoseData poseData;
    private int currentFrame = 0;
    private float timer = 0f;
    
    void Start()
    {
        LoadPoseData();
    }
    
    void LoadPoseData()
    {
        string jsonContent = File.ReadAllText(jsonFilePath);
        poseData = JsonUtility.FromJson<PoseData>(jsonContent);
        Debug.Log($"Loaded {poseData.total_frames} poses");
    }
    
    void Update()
    {
        if (poseData == null || poseData.poses.Count == 0)
            return;
        
        timer += Time.deltaTime;
        
        if (timer >= 1f / frameRate)
        {
            timer = 0f;
            ApplyPose(currentFrame);
            currentFrame = (currentFrame + 1) % poseData.poses.Count;
        }
    }
    
    void ApplyPose(int frameIndex)
    {
        List<float> pose = poseData.poses[frameIndex];
        
        // Convert flat array to 33 joints × 3 coordinates
        Vector3[] joints = new Vector3[33];
        for (int i = 0; i < 33; i++)
        {
            joints[i] = new Vector3(
                pose[i * 3],
                pose[i * 3 + 1],
                pose[i * 3 + 2]
            );
        }
        
        // Apply to character joints (MediaPipe joint indices)
        // 23 = left hip, 24 = right hip
        // 11 = left shoulder, 12 = right shoulder
        // 13 = left elbow, 14 = right elbow
        // 25 = left knee, 26 = right knee
        
        if (hipJoint != null)
        {
            Vector3 hipPos = (joints[23] + joints[24]) / 2f;
            hipJoint.localPosition = hipPos;
        }
        
        if (leftShoulderJoint != null)
            leftShoulderJoint.localPosition = joints[11];
        
        if (rightShoulderJoint != null)
            rightShoulderJoint.localPosition = joints[12];
        
        if (leftElbowJoint != null)
            leftElbowJoint.localPosition = joints[13];
        
        if (rightElbowJoint != null)
            rightElbowJoint.localPosition = joints[14];
        
        if (leftKneeJoint != null)
            leftKneeJoint.localPosition = joints[25];
        
        if (rightKneeJoint != null)
            rightKneeJoint.localPosition = joints[26];
    }
}
